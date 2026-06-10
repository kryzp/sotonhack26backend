export const API_BASE_URL = 'http://45.77.226.167:8000';

import type { GameResponse, RoundResponse } from './types';

export const api = {
  async createGame(
    rounds: number = 3,
    mode: 'team' | 'individual' = 'team',
    difficulty: string = 'medium',
    teamLeftName: string = 'Team Left',
    teamRightName: string = 'Team Right',
  ): Promise<GameResponse> {
    const response = await fetch(`${API_BASE_URL}/games`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        rounds,
        mode,
        difficulty,
        team_left_name: teamLeftName,
        team_right_name: teamRightName,
      }),
    });
    if (!response.ok) throw new Error('Failed to create game');
    return response.json();
  },

  async getGame(gameId: number): Promise<GameResponse> {
    const response = await fetch(`${API_BASE_URL}/games/${gameId}`);
    if (!response.ok) throw new Error('Failed to fetch game');
    return response.json();
  },

  async startGame(gameId: number): Promise<GameResponse> {
    const response = await fetch(`${API_BASE_URL}/games/${gameId}/start`, { method: 'POST' });
    if (!response.ok) throw new Error('Failed to start game');
    return response.json();
  },

  async nextRound(gameId: number): Promise<RoundResponse> {
    const response = await fetch(`${API_BASE_URL}/games/${gameId}/next-round`, { method: 'POST' });
    if (!response.ok) throw new Error('Failed to advance to next round');
    return response.json();
  },

  async getCurrentRound(gameId: number): Promise<RoundResponse> {
    const response = await fetch(`${API_BASE_URL}/games/${gameId}/rounds/current`);
    if (!response.ok) throw new Error('Failed to fetch current round');
    return response.json();
  },

  async openBuzz(gameId: number): Promise<RoundResponse> {
    const response = await fetch(`${API_BASE_URL}/games/${gameId}/rounds/current/open-buzz`, { method: 'POST' });
    if (!response.ok) throw new Error('Failed to open buzz');
    return response.json();
  },

  async buzz(gameId: number, playerId: string): Promise<RoundResponse> {
    const tempTimestamp = new Date().toISOString();
    const response = await fetch(`${API_BASE_URL}/games/${gameId}/rounds/current/buzz`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, timestamp: tempTimestamp }),
    });
    if (!response.ok) throw new Error('Failed to buzz in or already locked');
    return response.json();
  },

  async selectSide(gameId: number, side: 'left' | 'right'): Promise<RoundResponse> {
    const response = await fetch(`${API_BASE_URL}/games/${gameId}/rounds/current/select-side`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ side }),
    });
    if (!response.ok) throw new Error('Failed to select side');
    return response.json();
  },

  async submitTranscript(gameId: number, transcript: string): Promise<RoundResponse> {
    const response = await fetch(`${API_BASE_URL}/games/${gameId}/rounds/current/transcript`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ transcript }),
    });
    if (!response.ok) throw new Error('Failed to submit transcript');
    return response.json();
  },

  async submitFinalAnswer(gameId: number, answer: string): Promise<RoundResponse> {
    const response = await fetch(`${API_BASE_URL}/games/${gameId}/rounds/current/final-answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answer }),
    });
    if (!response.ok) throw new Error('Failed to submit final answer');
    return response.json();
  },

  async validateRound(gameId: number): Promise<RoundResponse> {
    const response = await fetch(`${API_BASE_URL}/games/${gameId}/rounds/current/validate`, { method: 'POST' });
    if (!response.ok) throw new Error('Failed to validate round');
    return response.json();
  },

  async submitSecondTranscript(gameId: number, transcript: string): Promise<RoundResponse> {
    const response = await fetch(`${API_BASE_URL}/games/${gameId}/rounds/current/second-transcript`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ transcript }),
    });
    if (!response.ok) throw new Error('Failed to submit second transcript');
    return response.json();
  },

  async submitSecondAnswer(gameId: number, answer: string): Promise<RoundResponse> {
    const response = await fetch(`${API_BASE_URL}/games/${gameId}/rounds/current/second-final-answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answer }),
    });
    if (!response.ok) throw new Error('Failed to submit second answer');
    return response.json();
  },

  async validateSecondRound(gameId: number): Promise<RoundResponse> {
    const response = await fetch(`${API_BASE_URL}/games/${gameId}/rounds/current/validate-second`, { method: 'POST' });
    if (!response.ok) throw new Error('Failed to validate second round');
    return response.json();
  },

  async generateCommentary(gameId: number, event: string, context: Record<string, unknown> = {}): Promise<{ audioUrl: string | null; text: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/games/${gameId}/commentary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event, context }),
      });
      if (!response.ok) throw new Error('Commentary failed');

      const text = response.headers.get('X-Commentary-Text') || '';
      const blob = await response.blob();
      const audioUrl = blob.size > 0 ? URL.createObjectURL(blob) : null;

      return { audioUrl, text };
    } catch (err) {
      console.error('Commentary error:', err);
      return { audioUrl: null, text: '' };
    }
  },
};
