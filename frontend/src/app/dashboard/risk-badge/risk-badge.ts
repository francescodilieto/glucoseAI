import { Component, input } from '@angular/core';

import { RiskAssessment } from '../../core/models/glucose.model';

@Component({
  selector: 'app-risk-badge',
  standalone: true,
  templateUrl: './risk-badge.html',
  styleUrl: './risk-badge.scss',
})
export class RiskBadge {
  readonly risk = input<RiskAssessment | null>(null);
}
