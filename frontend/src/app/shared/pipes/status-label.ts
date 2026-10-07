import { Pipe, PipeTransform } from '@angular/core';

const LABELS: Record<string, string> = {
  pending: 'Pendiente',
  in_progress: 'En curso',
  finished: 'Finalizado'
};

@Pipe({ name: 'statusLabel' })
export class StatusLabelPipe implements PipeTransform {
  transform(value: string | null | undefined): string {
    if (!value) return '';
    return LABELS[value] ?? value;
  }
}