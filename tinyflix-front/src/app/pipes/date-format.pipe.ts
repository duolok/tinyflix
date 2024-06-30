import { Pipe, PipeTransform } from '@angular/core';
import { DatePipe } from '@angular/common';

@Pipe({
  name: 'dateFormat',
  standalone: true
})
export class DateFormatPipe implements PipeTransform {
  constructor(private datePipe: DatePipe) {}

  transform(value: string, format: string = 'dd-MM-yyyy'): string | null {
    return this.datePipe.transform(value, format);
  }

}
