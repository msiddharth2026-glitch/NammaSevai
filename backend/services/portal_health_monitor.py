"""
Automated Official Portal Health Monitor Service.

Periodically verifies availability, HTTP response status, redirects, and potential
domain migrations for all official government portals stored in the database.

CRITICAL ARCHITECTURAL GUARANTEE:
A successful HTTP 200 response NEVER automatically alters a scheme's content
verification status. Portal health monitoring (network availability) and
scheme-content verification (policy correctness) remain strictly separated.
"""

import time
import datetime
import logging
from urllib.parse import urlparse
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
from sqlalchemy.orm import Session

# Suppress SSL certificate warning logs during civic verification checks
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from ..models.source import OfficialSource, PortalHealthLog
from ..models.scheme import Scheme
from ..schemas.source import PortalHealthCheckResult, PortalHealthSummary

logger = logging.getLogger("nammasevai.portal_health")

USER_AGENT = "NammaSevai-BharatSevai-PortalHealthMonitor/2.0 (+https://bharatsevai.gov.in/civic-audit)"
REQUEST_TIMEOUT_SECONDS = (4, 6)  # (connect_timeout, read_timeout)

def create_resilient_session() -> requests.Session:
    """Create a configured requests session with modest retries and user-agent."""
    session = requests.Session()
    retries = Retry(
        total=1,
        backoff_factor=0.5,
        status_forcelist=[502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    })
    return session


def check_url_health(url: str, session: Optional[requests.Session] = None) -> Dict[str, Any]:
    """
    Independently inspect a single portal URL.
    Detects HTTP status, redirects, domain migrations, and latency.
    """
    if not url:
        return {
            "is_available": False,
            "http_status": None,
            "response_time_ms": None,
            "redirect_url": None,
            "domain_migration_detected": False,
            "error_message": "Empty or null URL"
        }

    sess = session or create_resilient_session()
    start_time = time.perf_counter()
    initial_parsed = urlparse(url)

    try:
        # Most government portals respond to GET better than HEAD
        response = sess.get(url, timeout=REQUEST_TIMEOUT_SECONDS, allow_redirects=True, verify=False)
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        
        status_code = response.status_code
        final_url = str(response.url)
        final_parsed = urlparse(final_url)

        has_redirect = bool(response.history)
        redirect_url = final_url if has_redirect else None

        # Check if root domain or host changed
        initial_host = initial_parsed.netloc.lower().split(":")[0]
        final_host = final_parsed.netloc.lower().split(":")[0]
        domain_migrated = False
        if has_redirect and initial_host != final_host:
            # Strip leading 'www.' for fair comparison
            init_clean = initial_host[4:] if initial_host.startswith("www.") else initial_host
            fin_clean = final_host[4:] if final_host.startswith("www.") else final_host
            if init_clean != fin_clean:
                domain_migrated = True

        # Government servers often return 200, 301, 302, 403 (for automated bots)
        # We consider reachable if HTTP status is < 400 or specifically 403 (WAF challenge)
        is_available = status_code < 400 or status_code == 403

        return {
            "is_available": is_available,
            "http_status": status_code,
            "response_time_ms": duration_ms,
            "redirect_url": redirect_url,
            "domain_migration_detected": domain_migrated,
            "error_message": None if is_available else f"HTTP {status_code}"
        }

    except requests.exceptions.Timeout:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        return {
            "is_available": False,
            "http_status": 0,
            "response_time_ms": duration_ms,
            "redirect_url": None,
            "domain_migration_detected": False,
            "error_message": "Connection or Read Timeout (Server did not respond within limit)"
        }
    except requests.exceptions.SSLError as ssl_err:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        return {
            "is_available": False,
            "http_status": 0,
            "response_time_ms": duration_ms,
            "redirect_url": None,
            "domain_migration_detected": False,
            "error_message": f"SSL Certificate Error: {str(ssl_err)[:100]}"
        }
    except requests.exceptions.ConnectionError as conn_err:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        return {
            "is_available": False,
            "http_status": 0,
            "response_time_ms": duration_ms,
            "redirect_url": None,
            "domain_migration_detected": False,
            "error_message": f"Network Name Resolution / Connection Failure: {str(conn_err)[:100]}"
        }
    except Exception as ex:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        return {
            "is_available": False,
            "http_status": 0,
            "response_time_ms": duration_ms,
            "redirect_url": None,
            "domain_migration_detected": False,
            "error_message": f"Health check failed: {str(ex)[:100]}"
        }


class PortalHealthMonitorService:
    """Service orchestrating batch and single portal health audits."""

    @staticmethod
    def run_health_checks(
        db: Session,
        scheme_ids: Optional[List[str]] = None,
        max_workers: int = 4
    ) -> PortalHealthSummary:
        """
        Executes automated health checks on all (or targeted) scheme official source portals.
        Records results to `OfficialSource` columns and `PortalHealthLog` table.
        """
        query = db.query(OfficialSource, Scheme).join(Scheme, OfficialSource.scheme_id == Scheme.id)
        if scheme_ids:
            query = query.filter(OfficialSource.scheme_id.in_(scheme_ids))
        
        targets = query.all()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        results: List[PortalHealthCheckResult] = []
        session = create_resilient_session()

        def _check_target(source: OfficialSource, scheme: Scheme):
            health = check_url_health(source.portal_url, session=session)
            return (source.scheme_id, scheme.name, source.portal_url, source.verification_status, health)

        # Threaded batch processing with rate limiting
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_target = {
                executor.submit(_check_target, src, sc): (src.scheme_id, sc.name)
                for src, sc in targets
            }

            for future in as_completed(future_to_target):
                try:
                    s_id, s_name, p_url, ver_status, health = future.result()
                    
                    # Update database OfficialSource record
                    src_rec = db.query(OfficialSource).filter(OfficialSource.scheme_id == s_id).first()
                    if src_rec:
                        src_rec.http_status = health["http_status"]
                        src_rec.last_health_check = now_iso
                        src_rec.health_response_time_ms = health["response_time_ms"]
                        src_rec.redirect_url = health["redirect_url"]
                        src_rec.domain_migration_detected = health["domain_migration_detected"]
                        src_rec.health_error = health["error_message"]

                    # Append to historical health log
                    log_entry = PortalHealthLog(
                        scheme_id=s_id,
                        portal_url=p_url,
                        checked_at=now_iso,
                        http_status=health["http_status"],
                        is_available=health["is_available"],
                        response_time_ms=health["response_time_ms"],
                        redirect_url=health["redirect_url"],
                        domain_migration_detected=health["domain_migration_detected"],
                        error_message=health["error_message"]
                    )
                    db.add(log_entry)

                    # Build schema result
                    res_item = PortalHealthCheckResult(
                        scheme_id=s_id,
                        scheme_name=s_name,
                        portal_url=p_url,
                        is_available=health["is_available"],
                        http_status=health["http_status"],
                        response_time_ms=health["response_time_ms"],
                        redirect_url=health["redirect_url"],
                        domain_migration_detected=health["domain_migration_detected"],
                        error_message=health["error_message"],
                        checked_at=now_iso,
                        content_verification_status=ver_status or "Verified"
                    )
                    results.append(res_item)

                except Exception as e:
                    logger.error(f"Error checking portal: {e}")

        db.commit()

        # Compute summary
        total = len(results)
        avail = sum(1 for r in results if r.is_available)
        unavail = sum(1 for r in results if not r.is_available)
        redirects = sum(1 for r in results if r.redirect_url is not None)
        migrations = sum(1 for r in results if r.domain_migration_detected)
        broken = [r for r in results if not r.is_available or r.domain_migration_detected]

        return PortalHealthSummary(
            total_checked=total,
            available_count=avail,
            unavailable_count=unavail,
            redirects_detected=redirects,
            domain_migrations_detected=migrations,
            last_check_time=now_iso,
            broken_portals=broken
        )

    @staticmethod
    def get_latest_summary(db: Session) -> PortalHealthSummary:
        """
        Retrieves current snapshot of portal health from stored OfficialSource states
        without triggering full re-scan.
        """
        sources_schemes = db.query(OfficialSource, Scheme).join(Scheme, OfficialSource.scheme_id == Scheme.id).all()
        
        results: List[PortalHealthCheckResult] = []
        last_check_time = None

        for src, sc in sources_schemes:
            if src.last_health_check:
                if not last_check_time or src.last_health_check > last_check_time:
                    last_check_time = src.last_health_check

            # Availability: HTTP status < 400 or 403, and no critical error
            is_avail = True
            if src.http_status is not None:
                is_avail = (src.http_status < 400 or src.http_status == 403) and src.http_status > 0
            elif src.health_error:
                is_avail = False

            item = PortalHealthCheckResult(
                scheme_id=src.scheme_id,
                scheme_name=sc.name,
                portal_url=src.portal_url,
                is_available=is_avail,
                http_status=src.http_status,
                response_time_ms=src.health_response_time_ms,
                redirect_url=src.redirect_url,
                domain_migration_detected=bool(src.domain_migration_detected),
                error_message=src.health_error,
                checked_at=src.last_health_check or "Never",
                content_verification_status=src.verification_status or "Verified"
            )
            results.append(item)

        total = len(results)
        avail = sum(1 for r in results if r.is_available and r.http_status is not None)
        unavail = sum(1 for r in results if not r.is_available and r.http_status is not None)
        redirects = sum(1 for r in results if r.redirect_url is not None)
        migrations = sum(1 for r in results if r.domain_migration_detected)
        broken = [r for r in results if not r.is_available and r.http_status is not None]

        return PortalHealthSummary(
            total_checked=total,
            available_count=avail,
            unavailable_count=unavail,
            redirects_detected=redirects,
            domain_migrations_detected=migrations,
            last_check_time=last_check_time,
            broken_portals=broken
        )
