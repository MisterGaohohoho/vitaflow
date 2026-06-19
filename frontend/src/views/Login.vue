<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from "vue"
import { useRouter, useRoute, RouterLink } from "vue-router"
import { useUserStore } from "@/stores/user"
import { registerApi, sendVerificationCodeApi } from "@/api/auth"
import Button from "@/components/ui/button/Button.vue"
import Input from "@/components/ui/input/Input.vue"
import Label from "@/components/ui/label/Label.vue"
import BrandLogo from "@/components/common/BrandLogo.vue"

const router = useRouter()
const route = useRoute()
const user = useUserStore()

const isRegister = ref(false)

// Login State
const loginEmail = ref("")
const loginPassword = ref("")
const loginError = ref("")

// Register State
const regForm = ref({ username: "", email: "", password: "", verification_code: "" })
const regError = ref("")
const codeSeconds = ref(0)
const sendingCode = ref(false)
let countdownTimer: number | undefined

onMounted(() => {
  if (route.path === '/register') {
    isRegister.value = true
  }
})

watch(() => route.path, (newPath) => {
  isRegister.value = newPath === '/register'
})

function toggleMode(targetPath: string) {
  router.push(targetPath)
}

async function handleLogin() {
  try {
    loginError.value = ""
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(loginEmail.value.trim())) {
      throw new Error("请输入正确的邮箱地址")
    }
    if (!loginPassword.value) throw new Error("请输入密码")
    await user.login(loginEmail.value, loginPassword.value)
    router.push("/resumes")
  } catch (e: any) {
    loginError.value = e.message
  }
}

async function sendCode() {
  try {
    regError.value = ""
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(regForm.value.email.trim())) {
      throw new Error("请输入正确的邮箱地址")
    }
    sendingCode.value = true
    await sendVerificationCodeApi(regForm.value.email)
    codeSeconds.value = 60
    countdownTimer = window.setInterval(() => {
      codeSeconds.value -= 1
      if (codeSeconds.value <= 0 && countdownTimer) {
        window.clearInterval(countdownTimer)
        countdownTimer = undefined
      }
    }, 1000)
  } catch (e: any) {
    regError.value = e.message
  } finally {
    sendingCode.value = false
  }
}

onUnmounted(() => {
  if (countdownTimer) window.clearInterval(countdownTimer)
})

async function handleRegister() {
  try {
    regError.value = ""
    if (regForm.value.username.trim().length < 2) throw new Error("用户名至少需要 2 个字符")
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(regForm.value.email.trim())) {
      throw new Error("请输入正确的邮箱地址")
    }
    if (regForm.value.password.length < 6) throw new Error("密码至少需要 6 个字符")
    if (!/^\d{6}$/.test(regForm.value.verification_code)) throw new Error("请输入 6 位邮箱验证码")
    await registerApi(regForm.value)
    // auto fill login form
    loginEmail.value = regForm.value.email
    loginPassword.value = regForm.value.password
    // reset register form
    regForm.value = { username: "", email: "", password: "", verification_code: "" }
    // auto switch to login
    router.push("/login")
  } catch (e: any) {
    regError.value = e.message
  }
}
</script>

<template>
  <div class="grid min-h-screen grid-cols-1 bg-white lg:grid-cols-2">
    <!-- Left Dark Panel -->
    <div class="relative hidden bg-zinc-950 p-12 text-white lg:flex lg:flex-col lg:justify-between overflow-hidden">
      <!-- subtle background decoration -->
      <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMSIgY3k9IjEiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wNSkiLz48L3N2Zz4=')] opacity-50 mix-blend-overlay"></div>
      
      <div class="relative z-10">
        <RouterLink to="/" class="inline-flex w-fit rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white">
          <BrandLogo tone="light" />
        </RouterLink>
      </div>
      
      <div class="relative z-10 max-w-lg">
        <h1 class="text-4xl sm:text-5xl font-medium tracking-tight leading-[1.15]">
          你的经历，<br />值得更好的表达。
        </h1>
        <p class="mt-6 text-lg text-zinc-400">
          从内容编辑到 AI 优化，再到 PDF 导出，让简历制作一步到位。
        </p>
      </div>
      
      <div class="relative z-10 flex flex-col gap-1">
        <p class="text-sm text-zinc-600">&copy; 2026 GeekZero</p>
        <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer" class="text-xs text-zinc-500 hover:text-zinc-400 transition-colors">
          鲁ICP备2023002307号-2
        </a>
      </div>
    </div>

    <!-- Right Form Area with Flip -->
    <div class="flex items-center justify-center p-4 sm:p-6 bg-white perspective-1000 relative">
      <!-- mobile logo -->
      <div class="absolute top-6 left-6 sm:top-8 sm:left-8 lg:hidden">
        <RouterLink to="/" class="inline-flex rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-900">
          <BrandLogo />
        </RouterLink>
      </div>

      <!-- Main Container (No Card Styling) -->
      <div class="relative w-full max-w-sm h-[590px] flip-container" :class="{ 'flipped': isRegister }">
        <!-- Flipper -->
        <div class="flipper w-full h-full relative transition-transform duration-700 ease-[cubic-bezier(0.4,0,0.2,1)]">
          <!-- Front: Login -->
          <div class="front absolute w-full h-full bg-white flex flex-col justify-center">
            <h1 class="text-2xl font-semibold text-zinc-900 tracking-tight">欢迎回来</h1>
            <p class="mt-2 text-sm text-zinc-500">使用邮箱登录你的工作台</p>
            
            <div class="mt-8 flex-1 space-y-5">
              <div>
                <Label class="text-zinc-700 text-xs font-medium">邮箱</Label>
                <Input v-model="loginEmail" type="email" placeholder="请输入邮箱" class="mt-1.5 focus:ring-zinc-900 focus:border-zinc-900 transition-all" />
              </div>
              <div>
                <Label class="text-zinc-700 text-xs font-medium">密码</Label>
                <Input v-model="loginPassword" type="password" placeholder="请输入密码" class="mt-1.5 focus:ring-zinc-900 focus:border-zinc-900 transition-all" @keyup.enter="handleLogin" />
              </div>
              <p v-if="loginError" class="text-sm text-red-500">{{ loginError }}</p>
              <Button class="w-full bg-zinc-900 hover:bg-zinc-800 text-white mt-4 h-11 transition-transform active:scale-95" @click="handleLogin">登录</Button>
            </div>
            
            <div class="mt-8 text-center text-sm">
              <span class="text-zinc-500">还没有账号？</span>
              <button @click="toggleMode('/register')" class="text-zinc-900 font-medium hover:underline focus:outline-none transition-colors">立即注册</button>
            </div>
          </div>
          
          <!-- Back: Register -->
          <div class="back absolute w-full h-full bg-white flex flex-col justify-center">
            <h1 class="text-2xl font-semibold text-zinc-900 tracking-tight">创建账号</h1>
            <p class="mt-2 text-sm text-zinc-500">只需几秒，开启你的极简简历之旅</p>
            
            <div class="mt-8 flex-1 space-y-4">
              <div>
                <Label class="text-zinc-700 text-xs font-medium">用户名</Label>
                <Input v-model="regForm.username" placeholder="你的称呼" class="mt-1.5 focus:ring-zinc-900 focus:border-zinc-900 transition-all" />
              </div>
              <div>
                <Label class="text-zinc-700 text-xs font-medium">邮箱</Label>
                <Input v-model="regForm.email" placeholder="你的邮箱" class="mt-1.5 focus:ring-zinc-900 focus:border-zinc-900 transition-all" />
              </div>
              <div>
                <Label class="text-zinc-700 text-xs font-medium">密码</Label>
                <Input v-model="regForm.password" type="password" placeholder="设置密码" class="mt-1.5 focus:ring-zinc-900 focus:border-zinc-900 transition-all" @keyup.enter="handleRegister" />
              </div>
              <div>
                <Label class="text-zinc-700 text-xs font-medium">邮箱验证码</Label>
                <div class="mt-1.5 flex gap-2">
                  <Input v-model="regForm.verification_code" inputmode="numeric" maxlength="6" placeholder="6 位验证码" class="focus:ring-zinc-900 focus:border-zinc-900 transition-all" />
                  <Button type="button" variant="outline" class="w-32 shrink-0" :disabled="sendingCode || codeSeconds > 0" @click="sendCode">
                    {{ codeSeconds > 0 ? `${codeSeconds} 秒后重发` : (sendingCode ? "发送中..." : "发送验证码") }}
                  </Button>
                </div>
              </div>
              <p v-if="regError" class="text-sm text-red-500">{{ regError }}</p>
              <Button class="w-full bg-zinc-900 hover:bg-zinc-800 text-white mt-2 h-11 transition-transform active:scale-95" @click="handleRegister">注册</Button>
            </div>
            
            <div class="mt-8 text-center text-sm">
              <span class="text-zinc-500">已有账号？</span>
              <button @click="toggleMode('/login')" class="text-zinc-900 font-medium hover:underline focus:outline-none transition-colors">直接登录</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.perspective-1000 {
  perspective: 1000px;
}
.flipper {
  transform-style: preserve-3d;
}
.flip-container.flipped .flipper {
  transform: rotateY(-180deg);
}
.front, .back {
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}
.front {
  transform: rotateY(0deg);
}
.back {
  transform: rotateY(180deg);
}
</style>
