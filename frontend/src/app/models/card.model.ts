export interface Card {
  id: number;
  name: string;
  type: 'ataque' | 'defensa' | 'especial';
  value: number;
  effect: string;
  copiesAvailable: number;
  description: string;
  rarity: string;
}