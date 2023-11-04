import { AfterViewInit, Component } from '@angular/core';
import { Map, latLng, map, tileLayer } from 'leaflet';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements AfterViewInit {
  options = {
    layers: [
      tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution:
          '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      }),
    ],
    zoom: 10,
    center: latLng(31.4, 34.4),
  };

  private map!: Map;

  ngAfterViewInit(): void {
    this.initMap();
  }

  private initMap(): void {
    // tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    this.map = map('map');
    tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(
      this.map
    );
  }
}
