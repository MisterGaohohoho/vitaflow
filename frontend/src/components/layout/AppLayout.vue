<script setup lang="ts">
import { RouterLink, useRouter, useRoute } from "vue-router"
import { computed, onMounted } from "vue"
import { LayoutTemplate, Files, LogOut, Sparkles, UserRound } from "lucide-vue-next"
import Button from "@/components/ui/button/Button.vue"
import BrandLogo from "@/components/common/BrandLogo.vue"
import { useUserStore } from "@/stores/user"

const user = useUserStore()
const router = useRouter()
const route = useRoute()
const loggedIn = computed(() => Boolean(user.token))

onMounted(() => {
  if (user.token && !user.userInfo) user.getUserInfo().catch(() => user.logout())
})

function logout() {
  user.logout()
  router.push("/")
}
</script>

<template>
  <div class="min-h-screen bg-zinc-50/50">
    <header class="sticky top-0 z-20 border-b border-zinc-200/60 bg-white/80 backdrop-blur-md">
      <div class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        <RouterLink to="/" class="inline-flex items-center rounded-lg transition-opacity hover:opacity-80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-500">
          <BrandLogo />
        </RouterLink>
        
        <nav class="flex items-center gap-1 sm:gap-2 text-sm font-medium text-zinc-600">
          <RouterLink 
            class="flex items-center gap-1.5 rounded-md px-3 py-2 transition-colors hover:bg-zinc-100 hover:text-zinc-900" 
            :class="{ 'bg-zinc-100 text-zinc-900': route.path === '/templates' }"
            to="/templates"
          >
            <LayoutTemplate class="h-4 w-4" />
            <span class="hidden sm:inline">模板中心</span>
          </RouterLink>
          
          <template v-if="loggedIn">
            <RouterLink 
              class="flex items-center gap-1.5 rounded-md px-3 py-2 transition-colors hover:bg-zinc-100 hover:text-zinc-900" 
              :class="{ 'bg-zinc-100 text-zinc-900': route.path === '/resumes' }"
              to="/resumes"
            >
              <Files class="h-4 w-4" />
              <span class="hidden sm:inline">我的简历</span>
            </RouterLink>
            <RouterLink
              class="flex items-center gap-1.5 rounded-md px-3 py-2 transition-colors hover:bg-zinc-100 hover:text-zinc-900"
              :class="{ 'bg-zinc-100 text-zinc-900': route.path === '/profile' }"
              to="/profile"
            >
              <UserRound class="h-4 w-4" />
              <span class="hidden sm:inline">{{ user.userInfo?.username || '用户信息' }}</span>
            </RouterLink>
            <button 
              class="flex items-center gap-1.5 rounded-md px-3 py-2 text-zinc-500 transition-colors hover:bg-red-50 hover:text-red-600" 
              @click="logout"
            >
              <LogOut class="h-4 w-4" />
              <span class="hidden sm:inline">退出登录</span>
            </button>
          </template>
          
          <template v-else>
            <RouterLink to="/resumes" class="ml-1 sm:ml-2 shrink-0">
              <Button size="sm" class="h-9 px-3 sm:px-4 bg-zinc-900 text-white hover:bg-zinc-800 transition-all active:scale-95 shadow-sm rounded-lg shrink-0">
                <Sparkles class="h-4 w-4 mr-1 sm:mr-1.5 shrink-0" />
                <span class="whitespace-nowrap">开始使用</span>
              </Button>
            </RouterLink>
          </template>
        </nav>
      </div>
    </header>
    <slot />
  </div>
</template>
