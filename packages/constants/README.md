# @vben/constants

用于多个 `app` 公用的常量，继承了 `@vben-core/shared/constants` 的所有能力。适合放路由路径、应用元信息、存储 key、默认语言这类稳定共享值。

## 用法

### 添加依赖

```bash
# 进入目标应用目录，例如 apps/xxxx-app
# cd apps/xxxx-app
pnpm add @vben/constants
```

### 使用

```ts
import {
  ACCESS_TOKEN_KEY,
  APP_NAME,
  DEFAULT_HOME_PATH,
  DEFAULT_LANGUAGE,
  LOGIN_PATH,
} from '@vben/constants';
```

当前额外提供的常量包括：

- `LOGIN_PATH` / `ROOT_PATH` / `DEFAULT_HOME_PATH`
- `APP_NAME` / `APP_DESCRIPTION`
- `ACCESS_TOKEN_KEY` / `REFRESH_TOKEN_KEY`
- `LOCALE_KEY` / `THEME_MODE_KEY`
- `SUPPORT_LANGUAGES` / `DEFAULT_LANGUAGE`
