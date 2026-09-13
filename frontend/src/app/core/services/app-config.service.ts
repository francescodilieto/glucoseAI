import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import { environment } from '../../../environments/environment';

/**
 * Loads the backend URL from /config.json at startup, generated at container
 * start time from public/config.template.json (see frontend/Dockerfile).
 * This lets the same built image point at a different backend per
 * environment (docker-compose vs Render) without rebuilding.
 *
 * Falls back to environment.apiBaseUrl when config.json isn't present
 * (e.g. `ng serve`, where nothing generates it).
 */
@Injectable({ providedIn: 'root' })
export class AppConfigService {
  private readonly http = inject(HttpClient);

  apiBaseUrl: string = environment.apiBaseUrl;

  async load(): Promise<void> {
    try {
      const config = await firstValueFrom(this.http.get<{ apiBaseUrl: string }>('/config.json'));
      if (config?.apiBaseUrl && !config.apiBaseUrl.startsWith('${')) {
        this.apiBaseUrl = config.apiBaseUrl;
      }
    } catch {
      // No config.json (e.g. `ng serve`) -- keep the environment default.
    }
  }
}
