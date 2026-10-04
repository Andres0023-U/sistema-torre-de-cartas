export interface Deck {
  deckId: number;
  playerId: number;
  name: string;
}

export interface DeckCreate {
  name: string;
}

export interface DeckCard {
  deckId: number;
  cardId: number;
  quantity: number;
}

export interface Card {
  cardId: number;
  cardName: string;
  value: number;
  type: string;
  effect: string | null;
  maxQuantity: number;
  rarity: string;
  description: string;
}