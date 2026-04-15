/**
 * @zh_CN 登录页面 url 地址
 */
export const LOGIN_PATH = '/auth/login';
export const ROOT_PATH = '/';
export const DEFAULT_HOME_PATH = '/dashboard/analytics';

export const APP_NAME = 'Guard Silver Console';
export const APP_DESCRIPTION = 'A toy but serious multi-role anti-fraud admin workspace.';

export const STORAGE_PREFIX = 'guard-silver';
export const ACCESS_TOKEN_KEY = `${STORAGE_PREFIX}-access-token`;
export const REFRESH_TOKEN_KEY = `${STORAGE_PREFIX}-refresh-token`;
export const LOCALE_KEY = `${STORAGE_PREFIX}-locale`;
export const THEME_MODE_KEY = `${STORAGE_PREFIX}-theme-mode`;

export interface LanguageOption {
  label: string;
  value: 'en-US' | 'zh-CN';
}

/**
 * Supported languages
 */
export const SUPPORT_LANGUAGES: LanguageOption[] = [
  {
    label: '简体中文',
    value: 'zh-CN',
  },
  {
    label: 'English',
    value: 'en-US',
  },
];

export const DEFAULT_LANGUAGE: LanguageOption['value'] = 'zh-CN';
