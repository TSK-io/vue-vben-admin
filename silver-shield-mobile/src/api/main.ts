import { request } from '@/api/http'
import { backendModules } from '@/api/modules'
import { appConfig } from '@/utils/config'
import type {
  BackendUserRole,
  Contact,
  ElderProfile,
  LoginForm,
  RiskRecord,
  UserProfile,
  UserRole,
} from '@/types/app'

export interface AuthLoginResponse {
  token: string
  user: UserProfile
}

export interface BindingResponse {
  contacts: Contact[]
  elders: ElderProfile[]
}

export interface AlertListResponse {
  records: RiskRecord[]
}

interface RequestWithFallbackResult<T> {
  data: T
  fallback: boolean
}

interface BackendLoginResponse {
  access_token: string
  display_name: string
  expires_in: number
  refresh_token: string
  roles: BackendUserRole[]
  token_type: string
  user_id: string
  username: string
}

interface BackendProfileResponse {
  display_name: string
  permissions: string[]
  phone: string
  roles: BackendUserRole[]
  user_id: string
  username: string
}

interface BackendBindingItem {
  authorized_at: string
  elder_name: string
  elder_user_id: string
  family_name: string
  family_user_id: string
  id: string
  is_emergency_contact: boolean
  relationship_type: string
  status: string
}

interface BackendRiskAlertItem {
  elder_name: string
  elder_user_id: string
  id: string
  occurred_at: string
  risk_level: 'high' | 'low' | 'medium'
  risk_score: number
  source_type: 'call' | 'sms'
  status: string
  summary: string
  title: string
}

interface BackendRiskAlertDetail extends BackendRiskAlertItem {
  hit_rule_codes: string[]
  reason_detail: string
  suggestion_action: string
}

function mockProfileByRole(role: UserRole): UserProfile {
  if (role === 'elder') {
    return {
      id: 'elder-001',
      name: '王阿姨',
      role,
      phone: '138****1024',
      welcomeText: '今天也由我来守护您，遇到可疑消息先别着急。',
    }
  }

  return {
    id: 'guardian-001',
    name: '李女士',
    role,
    phone: '139****7718',
    welcomeText: '今天有 1 条高风险提醒待查看，另有 1 条求助需要优先回访。',
  }
}

function mockBindings(): BindingResponse {
  return {
    contacts: [
      {
        id: 'guardian-li',
        name: '李女士',
        relation: '女儿 / 守护人',
        avatarText: '李',
        isGuardian: true,
        tag: '优先联系',
        note: '收到风险提醒后会优先回拨。',
      },
      {
        id: 'elder-001',
        name: '王阿姨',
        relation: '母亲',
        avatarText: '王',
        tag: '高风险关注',
        note: '今天上午出现“养老金补缴”诈骗话术，需要回访确认。',
      },
      {
        id: 'elder-002',
        name: '赵叔叔',
        relation: '父亲',
        avatarText: '赵',
        tag: '今日已提醒',
        note: '下午已发送按时吃药提醒，晚间建议再联系一次。',
      },
      {
        id: 'neighbour-chen',
        name: '陈叔叔',
        relation: '邻居',
        avatarText: '陈',
        tag: '熟人',
        note: '经常帮忙买菜。',
      },
      {
        id: 'community-zhang',
        name: '张社工',
        relation: '社区网格员',
        avatarText: '张',
        tag: '社区',
        note: '紧急情况可协助上门核实。',
      },
    ],
    elders: [
      {
        id: 'elder-001',
        name: '王阿姨',
        age: 68,
        relation: '母亲',
        statusSummary: '今天上午触发 1 条高风险提醒，暂未再次点击陌生链接。',
        lastContactAt: '今天 09:26',
        lastRiskAt: '今天 09:21',
        riskLevel: 'high',
        riskCountToday: 1,
        pendingAlerts: 1,
        hasActiveSos: true,
        medicationNote: '晚饭后降压药待确认是否已服用。',
      },
      {
        id: 'elder-002',
        name: '赵叔叔',
        age: 71,
        relation: '父亲',
        statusSummary: '状态稳定，下午收到一次服药提醒并已回复。',
        lastContactAt: '今天 15:10',
        riskLevel: 'low',
        riskCountToday: 0,
        pendingAlerts: 0,
        medicationNote: '20:00 前提醒测量血压。',
      },
    ],
  }
}

function mockAlerts(): AlertListResponse {
  return {
    records: [
      {
        id: 'risk-1',
        level: 'high',
        title: '老人端实时风险提醒',
        summary: '聊天中出现“转账到安全账户”和“验证码核验”等高危话术。',
        reason: '命中转账、验证码等强风险词，并带有强操作诱导。',
        suggestion: '立即联系老人停止操作，并回访确认是否已泄露验证码。',
        time: '今天 09:21',
        source: 'chat',
        matchedText: ['转账', '验证码', '安全账户'],
        confidence: 0.91,
        traceKey: 'message-msg-risk-seed',
        detectionStatus: 'fallback',
      },
    ],
  }
}

function normalizeUserRole(role: BackendUserRole): UserRole {
  return role === 'family' ? 'guardian' : 'elder'
}

function buildWelcomeText(role: UserRole, name: string) {
  if (role === 'elder') {
    return `${name}，遇到转账、验证码、陌生链接时，先暂停，再联系家人确认。`
  }

  return `${name}，请优先处理高风险提醒、回访老人，并关注最新求助。`
}

function mapBackendProfile(profile: BackendProfileResponse): UserProfile {
  const primaryRole = normalizeUserRole(profile.roles[0] || 'elder')

  return {
    id: profile.user_id,
    name: profile.display_name,
    role: primaryRole,
    phone: profile.phone,
    welcomeText: buildWelcomeText(primaryRole, profile.display_name),
    backendRoles: profile.roles,
    username: profile.username,
  }
}

function normalizeTimeLabel(value?: string) {
  if (!value) {
    return '待更新'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  return date.toLocaleString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    month: '2-digit',
    day: '2-digit',
    hour12: false,
  })
}

async function requestWithFallback<T>(
  run: () => Promise<T>,
  fallback: () => T,
): Promise<RequestWithFallbackResult<T>> {
  try {
    if (appConfig.appEnv === 'demo') {
      return {
        data: fallback(),
        fallback: true,
      }
    }

    return {
      data: await run(),
      fallback: false,
    }
  } catch {
    return {
      data: fallback(),
      fallback: true,
    }
  }
}

export function loginByPassword(form: LoginForm): Promise<RequestWithFallbackResult<AuthLoginResponse>> {
  return requestWithFallback(
    () =>
      request<BackendLoginResponse>({
        url: backendModules.main.login,
        method: 'POST',
        data: {
          username: form.account,
          password: form.password,
        },
      }).then((result) => {
        const role = normalizeUserRole(result.roles[0] || 'elder')
        return {
          token: result.access_token,
          user: {
            id: result.user_id,
            name: result.display_name,
            role,
            phone: '',
            welcomeText: buildWelcomeText(role, result.display_name),
            backendRoles: result.roles,
            username: result.username,
          },
        }
      }),
    () => ({
      token: `mock-token-${form.role}`,
      user: mockProfileByRole(form.role),
    }),
  )
}

export function fetchUserProfile(role: UserRole): Promise<RequestWithFallbackResult<UserProfile>> {
  return requestWithFallback(
    () =>
      request<BackendProfileResponse>({
        url: backendModules.main.profile,
      }).then((result) => mapBackendProfile(result)),
    () => mockProfileByRole(role),
  )
}

export function fetchBindingRelations(): Promise<RequestWithFallbackResult<BindingResponse>> {
  return requestWithFallback(
    () =>
      request<BackendBindingItem[]>({
        url: backendModules.main.binding,
      }).then((rows) => {
        const contacts = rows.map(
          (item): Contact => ({
            id: item.family_user_id,
            name: item.family_name,
            relation: item.relationship_type,
            avatarText: item.family_name?.slice(0, 1) || '家',
            isGuardian: true,
            isPriority: item.is_emergency_contact,
            tag: item.is_emergency_contact ? '紧急联系人' : '家庭联系人',
            note: item.status === 'active' ? '当前绑定已生效。' : `当前状态：${item.status}`,
          }),
        )

        const eldersMap = new Map<string, ElderProfile>()
        for (const item of rows) {
          if (!eldersMap.has(item.elder_user_id)) {
            eldersMap.set(item.elder_user_id, {
              id: item.elder_user_id,
              name: item.elder_name,
              age: 0,
              relation: item.relationship_type,
              statusSummary: item.status === 'active' ? '监护关系正常。' : `绑定状态：${item.status}`,
              lastContactAt: normalizeTimeLabel(item.authorized_at),
              riskLevel: 'low',
              riskCountToday: 0,
              pendingAlerts: 0,
            })
          }
        }

        return {
          contacts,
          elders: [...eldersMap.values()],
        }
      }),
    mockBindings,
  )
}

export function fetchRiskAlerts(): Promise<RequestWithFallbackResult<AlertListResponse>> {
  return requestWithFallback(
    () =>
      request<{
        items: BackendRiskAlertItem[]
        pagination: {
          page: number
          page_size: number
          total: number
        }
      }>({
        url: backendModules.main.alerts,
        params: {
          page: 1,
          page_size: 20,
        },
      }).then(async (result) => {
        const details = await Promise.all(
          result.items.map((item) =>
            request<BackendRiskAlertDetail>({
              url: `${backendModules.main.alertDetail}/${item.id}`,
            }),
          ),
        )

        return {
          records: result.items.map(
            (item, index): RiskRecord => ({
              id: item.id,
              level: item.risk_level,
              title: item.title,
              summary: item.summary,
              reason: details[index]?.reason_detail,
              suggestion: details[index]?.suggestion_action,
              time: normalizeTimeLabel(item.occurred_at),
              source: item.source_type === 'sms' ? 'chat' : 'call',
              matchedText: details[index]?.hit_rule_codes || [],
              confidence: Math.min((item.risk_score || 0) / 100, 1),
              traceKey: item.id,
              detectionStatus: 'success',
              relatedContactId: item.elder_user_id,
              followUpStatus: item.status === 'closed' ? 'resolved' : 'pending',
            }),
          ),
        }
      }),
    mockAlerts,
  )
}
