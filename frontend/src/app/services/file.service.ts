import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class FileService {
  constructor(private http: HttpClient) { }

  readJsonFile(fileUrl: string) {
    return this.http.get(fileUrl);
  }
}
