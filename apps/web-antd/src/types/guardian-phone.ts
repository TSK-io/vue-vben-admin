export type GuardianRole = 'admin' | 'community' | 'elder' | 'family' | 'input';

export type CommunicationScene = 'call' | 'sms';

export type PhoneTrustType = 'blacklisted' | 'self' | 'trusted' | 'unknown';

export type RiskLevel = 'high' | 'low' | 'medium';

export interface PhoneIdentity {
  displayName: string;
  phone: string;
  role: GuardianRole;
  userId?: string;
}

export interface PhoneDirectoryUser {
  displayName: string;
  phone: string;
  roles: GuardianRole[];
  status: string;
  userId: string;
  username: string;
}

export interface TrustedContact {
  contactName: string;
  contactPhone: string;
  contactRole?: 'community' | 'family' | 'friend' | 'spouse';
  elderPhone: string;
  id: string;
  isEmergencyContact: boolean;
  relationshipType: string;
  source: 'binding' | 'manual' | 'seed';
}

export interface BlockedNumber {
  createdAt: string;
  elderPhone: string;
  id: string;
  phone: string;
  reason: string;
  riskEventId?: string;
  source: 'auto-risk' | 'manual';
}

export interface RiskDecision {
  alertId?: null | string;
  autoBlocked: boolean;
  hitRuleCodes: string[];
  hitTerms: string[];
  reasonDetail: string;
  recordId: string;
  riskLevel: RiskLevel | string;
  riskScore: number;
  scene: string;
  suggestionAction: string;
  workorderId?: null | string;
}

export interface CommunicationEvent {
  callSessionId?: string;
  contentText?: string;
  createdAt: string;
  durationSeconds?: number;
  elderUserId: string;
  id: string;
  operatorUserId?: string;
  risk?: RiskDecision;
  scene: CommunicationScene;
  sourcePhone: string;
  status:
    | 'delivered'
    | 'ended'
    | 'failed'
    | 'intercepted'
    | 'pending'
    | 'recognizing'
    | 'ringing';
  targetPhone: string;
  trustType: PhoneTrustType;
  updatedAt: string;
}
