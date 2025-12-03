# Implementación de Tabs Dinámicos por Rol de Usuario

## ✅ Backend Completado

### Endpoint: `GET /api/v1/profiles/me`

**Respuesta actualizada:**
```json
{
  "id": "uuid-del-usuario",
  "reputation_score": 100,
  "points_current": 50,
  "roles": ["VENUE_OWNER", "SUPER_ADMIN"]
}
```

**Roles posibles:**
- `SUPER_ADMIN` - Administrador del sistema
- `VENUE_OWNER` - Dueño de al menos un local
- `VENUE_MANAGER` - Manager de un local
- `VENUE_STAFF` - Staff de un local
- `APP_PREMIUM_USER` - Usuario premium
- `APP_USER` - Usuario normal (por defecto)

---

## 🎨 Frontend: Implementación de Tabs Dinámicos

### 1. Hook para detectar roles del usuario

Crea `src/hooks/useUserRoles.ts`:

```typescript
import { useProfile } from './useProfile';

export type UserRole = 
  | 'SUPER_ADMIN'
  | 'VENUE_OWNER'
  | 'VENUE_MANAGER'
  | 'VENUE_STAFF'
  | 'APP_PREMIUM_USER'
  | 'APP_USER';

export function useUserRoles() {
  const { data: profile, isLoading } = useProfile();
  
  const roles = profile?.roles || [];
  
  const hasRole = (role: UserRole) => roles.includes(role);
  
  const hasAnyRole = (checkRoles: UserRole[]) => 
    checkRoles.some(role => roles.includes(role));
  
  const isB2BUser = hasAnyRole([
    'SUPER_ADMIN',
    'VENUE_OWNER',
    'VENUE_MANAGER',
    'VENUE_STAFF'
  ]);
  
  const isSuperAdmin = hasRole('SUPER_ADMIN');
  
  const isVenueOwner = hasRole('VENUE_OWNER');
  
  return {
    roles,
    hasRole,
    hasAnyRole,
    isB2BUser,
    isSuperAdmin,
    isVenueOwner,
    isLoading
  };
}
```

---

### 2. Actualizar `useProfile` hook

Modifica `src/hooks/useProfile.ts`:

```typescript
import { useQuery } from '@tanstack/react-query';
import { client } from '../api/client';

export interface UserProfile {
  id: string;
  reputation_score: number;
  points_current: number;
  roles: string[];  // ✅ NUEVO
}

async function fetchProfile(): Promise<UserProfile> {
  const res = await client.get('/profiles/me');
  return res.data;
}

export function useProfile() {
  return useQuery<UserProfile>({
    queryKey: ['profile', 'me'],
    queryFn: fetchProfile,
    staleTime: 60_000,
  });
}
```

---

### 3. Configurar tabs dinámicos

Crea `src/config/tabs.config.ts`:

```typescript
import { UserRole } from '../hooks/useUserRoles';

export interface TabConfig {
  name: string;
  href: string;
  icon: string;
  requiredRoles?: UserRole[];
}

export const ALL_TABS: TabConfig[] = [
  {
    name: 'Explorar',
    href: '/(user)/(tabs)/index',
    icon: 'compass',
    // Disponible para todos
  },
  {
    name: 'Lista',
    href: '/(user)/(tabs)/list',
    icon: 'list',
    // Disponible para todos
  },
  {
    name: 'Mis Locales',
    href: '/(user)/(tabs)/my-venues',
    icon: 'store',
    requiredRoles: ['VENUE_OWNER', 'VENUE_MANAGER', 'VENUE_STAFF', 'SUPER_ADMIN']
  },
  {
    name: 'Admin Panel',
    href: '/(user)/(tabs)/admin',
    icon: 'shield',
    requiredRoles: ['SUPER_ADMIN']
  },
  {
    name: 'Perfil',
    href: '/(user)/(tabs)/profile',
    icon: 'person',
    // Disponible para todos
  },
];

export function getTabsForUser(userRoles: string[]): TabConfig[] {
  return ALL_TABS.filter(tab => {
    // Si no requiere roles específicos, mostrar siempre
    if (!tab.requiredRoles || tab.requiredRoles.length === 0) {
      return true;
    }
    
    // Verificar si el usuario tiene al menos uno de los roles requeridos
    return tab.requiredRoles.some(role => userRoles.includes(role));
  });
}
```

---

### 4. Componente de Tabs Dinámicos

Crea `src/components/DynamicTabs.tsx`:

```typescript
import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { useRouter, usePathname } from 'expo-router';
import { useUserRoles } from '../hooks/useUserRoles';
import { getTabsForUser } from '../config/tabs.config';

export function DynamicTabs() {
  const router = useRouter();
  const pathname = usePathname();
  const { roles, isLoading } = useUserRoles();
  
  if (isLoading) {
    return <View className="h-16 bg-surface" />;
  }
  
  const visibleTabs = getTabsForUser(roles);
  
  return (
    <View className="flex-row bg-surface border-t border-surface-active">
      {visibleTabs.map((tab) => {
        const isActive = pathname === tab.href;
        
        return (
          <TouchableOpacity
            key={tab.name}
            onPress={() => router.push(tab.href)}
            className={`flex-1 items-center justify-center py-3 ${
              isActive ? 'bg-primary/10' : ''
            }`}
          >
            {/* Aquí va tu ícono */}
            <Text className={`text-sm ${
              isActive ? 'text-primary font-bold' : 'text-foreground-muted'
            }`}>
              {tab.name}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}
```

---

### 5. Usar en el layout

Modifica `app/(user)/(tabs)/_layout.tsx`:

```typescript
import { DynamicTabs } from '../../../src/components/DynamicTabs';

export default function TabsLayout() {
  return (
    <View className="flex-1">
      {/* Tu contenido aquí */}
      <Slot />
      
      {/* Tabs dinámicos */}
      <DynamicTabs />
    </View>
  );
}
```

---

## 🧪 Ejemplos de Comportamiento

### Usuario APP_USER
```json
{
  "roles": ["APP_USER"]
}
```
**Tabs visibles:** Explorar, Lista, Perfil

---

### Usuario VENUE_OWNER
```json
{
  "roles": ["VENUE_OWNER", "APP_USER"]
}
```
**Tabs visibles:** Explorar, Lista, **Mis Locales**, Perfil

---

### Usuario SUPER_ADMIN
```json
{
  "roles": ["SUPER_ADMIN", "VENUE_OWNER"]
}
```
**Tabs visibles:** Explorar, Lista, **Mis Locales**, **Admin Panel**, Perfil

---

## 🔒 Protección de Rutas

Crea un guard para proteger rutas B2B:

```typescript
// src/guards/B2BGuard.tsx
import { useUserRoles } from '../hooks/useUserRoles';
import { Redirect } from 'expo-router';

export function B2BGuard({ children }: { children: React.ReactNode }) {
  const { isB2BUser, isLoading } = useUserRoles();
  
  if (isLoading) {
    return <LoadingScreen />;
  }
  
  if (!isB2BUser) {
    return <Redirect href="/(user)/(tabs)/index" />;
  }
  
  return <>{children}</>;
}
```

Úsalo en rutas protegidas:

```typescript
// app/(user)/(tabs)/my-venues.tsx
import { B2BGuard } from '../../../src/guards/B2BGuard';

export default function MyVenuesScreen() {
  return (
    <B2BGuard>
      {/* Contenido solo para usuarios B2B */}
    </B2BGuard>
  );
}
```

---

## ✅ Ventajas de esta Implementación

1. **Centralizado** - Un solo endpoint para roles
2. **Cacheable** - React Query cachea la respuesta
3. **Type-safe** - TypeScript para roles
4. **Reutilizable** - Hook `useUserRoles()` en cualquier componente
5. **Seguro** - Roles vienen del servidor, no del cliente
6. **Flexible** - Fácil agregar nuevos tabs o roles

---

## 🚀 Próximos Pasos

1. **Reinicia el servidor backend**
2. **Actualiza el frontend** con los hooks y componentes
3. **Prueba con diferentes usuarios:**
   - APP_USER → 3 tabs
   - VENUE_OWNER → 4 tabs
   - SUPER_ADMIN → 5 tabs
