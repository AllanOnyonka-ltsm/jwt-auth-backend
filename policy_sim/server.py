from __future__ import annotations

import json
import pathlib
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Mapping
from urllib.parse import urlparse

from .indicators import generate_pseudo_indicators
from .meal import generate_context_warnings
from .models import HistoricalPolicy, PolicyInput, SimulationConfig
from .simulate import run_monte_carlo


WEB_DIR = pathlib.Path(__file__).resolve().parent / "web"


class PolicySimHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: Mapping[str, Any], status: int = 200) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, path: pathlib.Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return
        content = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        if path.suffix == ".html":
            self.send_header("Content-Type", "text/html; charset=utf-8")
        elif path.suffix == ".js":
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
        elif path.suffix == ".css":
            self.send_header("Content-Type", "text/css; charset=utf-8")
        else:
            self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_file(WEB_DIR / "index.html")
            return
        if parsed.path.startswith("/static/"):
            target = WEB_DIR / parsed.path.replace("/static/", "", 1)
            self._send_file(target)
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/api/simulate":
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length)
        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
            return

        policy_payload = payload.get("policy", {})
        config_payload = payload.get("config", {})

        policy = PolicyInput(
            name=policy_payload.get("name", "Unnamed Policy"),
            tax_change=float(policy_payload.get("tax_change", 0.0)),
            subsidy_change=float(policy_payload.get("subsidy_change", 0.0)),
            transfer_change=float(policy_payload.get("transfer_change", 0.0)),
            metadata=policy_payload.get("metadata", {}),
        )
        config = SimulationConfig(
            baseline_gdp_growth=float(
                config_payload.get("baseline_gdp_growth", 0.02)
            ),
            baseline_inflation=float(config_payload.get("baseline_inflation", 0.03)),
            baseline_poverty_rate=float(
                config_payload.get("baseline_poverty_rate", 0.15)
            ),
            fiscal_multiplier=float(config_payload.get("fiscal_multiplier", 0.9)),
            inflation_sensitivity=float(
                config_payload.get("inflation_sensitivity", 0.4)
            ),
            poverty_elasticity=float(config_payload.get("poverty_elasticity", -0.6)),
            transfer_poverty_effect=float(
                config_payload.get("transfer_poverty_effect", -0.3)
            ),
            shock_std_gdp=float(config_payload.get("shock_std_gdp", 0.01)),
            shock_std_inflation=float(
                config_payload.get("shock_std_inflation", 0.008)
            ),
            shock_correlation=float(config_payload.get("shock_correlation", 0.35)),
        )

        simulations = int(payload.get("simulations", 2000))
        seed = payload.get("seed")

        historical_payload = payload.get("historical", [])
        historical = [
            HistoricalPolicy(
                name=item.get("name", "Historical Policy"),
                policy=policy,
                outcomes=item.get("outcomes", {}),
                metadata=item.get("metadata", {}),
            )
            for item in historical_payload
        ]

        result = run_monte_carlo(policy, config, simulations=simulations, seed=seed)
        warnings = generate_context_warnings(policy, historical)
        indicators = generate_pseudo_indicators(seed=seed)

        self._send_json(
            {
                "summary": result.summary,
                "notes": result.notes,
                "warnings": warnings,
                "indicators": indicators,
            }
        )


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = HTTPServer((host, port), PolicySimHandler)
    print(f"Policy simulation UI running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
