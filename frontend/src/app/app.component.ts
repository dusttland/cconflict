import { Component } from '@angular/core';
import * as L from 'leaflet';
import 'leaflet.heat';

import { testdata2 } from '../assets/testdata2';
import * as shelters from '../assets/shelters.json';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  options = {
    layers: [
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution:
          '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      }),
    ],
    zoom: 10,
    center: L.latLng(31.4, 34.4),
  };

  private map!: L.Map;
  private markers: Map<string, L.Marker[]> = new Map(
    Object.keys(shelters).map((key) => [key, []])
  );

  onMapReady(map: L.Map): void {
    this.map = map;

    let heatPoints = testdata2.features.map((feature) => {
      return [
        feature.geometry.coordinates[1],
        feature.geometry.coordinates[0],
        0.6, // intensity can be modified
      ] as L.HeatLatLngTuple;
    });
    L.heatLayer(heatPoints, { radius: 15 }).addTo(map); // radius can be modified

    Object.keys(shelters).forEach((shelterType) => {
      this.toggleShelterType(shelterType, true);
    });
  }

  toggleShelterType(type: string, event: boolean | Event): void {
    if (type === 'default') return;

    const data = shelters[type as keyof typeof shelters];
    const iconUrl = `../assets/${type}.svg`;
    const isChecked =
      event instanceof Event
        ? (event.target as HTMLInputElement).checked
        : event;
    console.log(isChecked);

    if (isChecked) {
      data.forEach((shelter) => {
        const marker = L.marker(
          L.latLng(+shelter.latitude, +shelter.longitude),
          {
            icon: L.icon({ iconUrl }),
          }
        ).addTo(this.map);

        marker.bindTooltip(shelter.name, {
          direction: 'top',
          offset: L.point(12, 0),
        });

        this.markers.get(type)?.push(marker);
      });
    } else {
      this.markers.get(type)?.forEach((marker) => {
        marker.remove();
      });
      this.markers.set(type, []);
    }
  }
}
