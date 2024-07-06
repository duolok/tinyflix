import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'roundTwoDecimals',
  standalone: true
})
export class RoundTwoDecimalsPipe implements PipeTransform {

  transform(value: number): number {
    if (isNaN(value)) {
      return value;
    }
    return Math.round(value * 10) / 10;
  }
}
