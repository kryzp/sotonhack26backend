from __future__ import annotations

import json
from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
	def __init__(self):
		self._connections: Dict[int, List[WebSocket]] = {}

	async def connect(self, game_id: int, ws: WebSocket) -> None:
		await ws.accept()
		self._connections.setdefault(game_id, []).append(ws)

	def disconnect(self, game_id: int, ws: WebSocket) -> None:
		conns = self._connections.get(game_id, [])
		if ws in conns:
			conns.remove(ws)

	async def broadcast(self, game_id: int, data: dict) -> None:
		conns = self._connections.get(game_id, [])
		dead: List[WebSocket] = []

		for ws in conns:
			try:
				await ws.send_text(json.dumps(data, default=str))
			except Exception:
				dead.append(ws)

		for ws in dead:
			self.disconnect(game_id, ws)

manager = ConnectionManager()
