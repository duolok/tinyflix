import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'peopleFormat',
  standalone: true
})
export class PeopleFormatPipe implements PipeTransform {

  transform(value: string): string {
    if (!value) {
      return '';
    }
    return value.split('|').join(', ');
  }

}
