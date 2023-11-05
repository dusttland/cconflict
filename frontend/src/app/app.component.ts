import { ChangeDetectorRef, Component } from '@angular/core';
import * as L from 'leaflet';
import 'leaflet.heat';
import { firstValueFrom } from 'rxjs';

import * as shelters from '../assets/shelters.json';
import { FileService } from './services/file.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  mapOptions = {
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
  showComparison = false;

  private map!: L.Map;
  private markers: Map<string, L.Marker[]> = new Map(
    Object.keys(shelters).map((key) => [key, []])
  );

  constructor(
    private readonly cd: ChangeDetectorRef,
    private readonly fs: FileService
  ) {}

  async onMapReady(map: L.Map): Promise<void> {
    this.map = map;

    const heatPoints = (<number[][]>await firstValueFrom(this.fs.readJsonFile('../assets/heat_map.json'))).filter((point) => {
      return point[2] > 0.32;
    }).map((point) => {
      return [point[0], point[1], point[2] * 2] as L.HeatLatLngTuple;
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
        marker.on('click', () => {
          this.showComparison = true;
          this.cd.detectChanges();
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

  closeComparison(): void {
    this.showComparison = false;
    this.cd.detectChanges();
  }
}
