<script setup lang="ts">
import { onMounted, ref, computed } from "vue"
import AppLayout from "@/components/layout/AppLayout.vue"
import Button from "@/components/ui/button/Button.vue"
import Input from "@/components/ui/input/Input.vue"
import Label from "@/components/ui/label/Label.vue"
import { changePasswordApi, updateProfileApi } from "@/api/auth"
import { useUserStore } from "@/stores/user"
import { Loader2, RefreshCw, CheckCircle2, AlertCircle } from "lucide-vue-next"

const user = useUserStore()
const username = ref("")
const profileSaving = ref(false)

const passwordForm = ref({ current_password: "", new_password: "", confirm_password: "" })
const passwordSaving = ref(false)

const isPasswordMode = ref(false)
const toastMessage = ref("")
const isToastError = ref(false)

function showToast(message: string, isError = false) {
  toastMessage.value = message
  isToastError.value = isError
  setTimeout(() => {
    if (toastMessage.value === message) {
      toastMessage.value = ""
    }
  }, 3000)
}

const userInitial = computed(() => {
  if (username.value) return username.value.charAt(0).toUpperCase()
  if (user.userInfo?.email) return user.userInfo.email.charAt(0).toUpperCase()
  return "U"
})

onMounted(async () => {
  if (!user.userInfo) await user.getUserInfo()
  username.value = user.userInfo?.username || ""
})

async function saveProfile() {
  try {
    profileSaving.value = true
    user.userInfo = await updateProfileApi({ username: username.value })
    showToast("用户名已成功更新")
  } catch (e: any) {
    showToast(e.message || "更新失败，请重试", true)
  } finally {
    profileSaving.value = false
  }
}

async function savePassword() {
  try {
    passwordSaving.value = true
    if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
      throw new Error("两次输入的新密码不一致")
    }
    if (passwordForm.value.new_password.length < 6) {
      throw new Error("新密码长度不能少于6位")
    }
    await changePasswordApi({
      current_password: passwordForm.value.current_password,
      new_password: passwordForm.value.new_password,
    })
    passwordForm.value = { current_password: "", new_password: "", confirm_password: "" }
    showToast("密码已成功修改")
  } catch (e: any) {
    showToast(e.message || "修改密码失败，请核对当前密码", true)
  } finally {
    passwordSaving.value = false
  }
}
</script>

<template>
  <AppLayout>
    <main class="mx-auto max-w-xl px-4 py-12 sm:px-6 flex flex-col items-center">
      
      <!-- Avatar & Header -->
      <div class="flex flex-col items-center justify-center text-center space-y-4 mb-10 perspective-1000">
        <div class="flex h-24 w-24 items-center justify-center rounded-full bg-zinc-200/50 text-4xl font-medium text-zinc-700 transition-transform duration-700" :style="{ transform: isPasswordMode ? 'rotateY(180deg)' : 'rotateY(0deg)' }">
          <span :style="{ transform: isPasswordMode ? 'rotateY(180deg)' : 'rotateY(0deg)' }" class="transition-transform duration-700 inline-block">{{ userInitial }}</span>
        </div>
        <div>
          <h1 class="text-2xl font-semibold text-zinc-900 tracking-tight">{{ username || 'Vita User' }}</h1>
          <p class="text-zinc-500 mt-1 text-sm">{{ user.userInfo?.email }}</p>
        </div>
      </div>

      <!-- Main Container (Flip) -->
      <div class="relative w-full max-w-sm mx-auto perspective-1000 flip-container" :class="{ 'flipped': isPasswordMode }">
        <div class="flipper grid w-full relative transition-transform duration-700 ease-[cubic-bezier(0.4,0,0.2,1)] items-start">
          
          <!-- Front: Profile -->
          <div class="front col-start-1 row-start-1 w-full flex flex-col justify-start pt-2" :class="isPasswordMode ? 'pointer-events-none' : ''">
            <div class="space-y-6">
              <div class="relative flex items-center justify-center">
                <h2 class="text-xl font-medium text-zinc-900 tracking-tight">基本信息</h2>
                <button @click="isPasswordMode = true" class="absolute right-0 flex items-center gap-1.5 text-sm text-zinc-500 hover:text-zinc-900 transition-colors focus:outline-none">
                  <RefreshCw class="w-3.5 h-3.5" />
                  <span>改密码</span>
                </button>
              </div>
              <div class="space-y-4">
                <div class="space-y-1.5">
                  <Label class="text-zinc-700 text-sm font-medium">登录邮箱</Label>
                  <Input :model-value="user.userInfo?.email || ''" disabled class="bg-zinc-50 border-zinc-200 text-zinc-500" />
                </div>
                <div class="space-y-1.5">
                  <Label class="text-zinc-700 text-sm font-medium">用户名</Label>
                  <Input v-model="username" maxlength="50" class="border-zinc-200 focus-visible:ring-zinc-900 transition-all" />
                </div>
              </div>
              
              <Button @click="saveProfile" :disabled="profileSaving" class="w-full bg-zinc-900 hover:bg-zinc-800 text-white mt-4 h-11 transition-transform active:scale-95">
                <Loader2 v-if="profileSaving" class="mr-2 h-4 w-4 animate-spin" />保存更改
              </Button>
            </div>
          </div>

          <!-- Back: Password -->
          <div class="back col-start-1 row-start-1 w-full flex flex-col justify-start pt-2" :class="!isPasswordMode ? 'pointer-events-none' : ''">
            <div class="space-y-6">
              <div class="relative flex items-center justify-center">
                <h2 class="text-xl font-medium text-zinc-900 tracking-tight">修改密码</h2>
                <button @click="isPasswordMode = false" class="absolute right-0 flex items-center gap-1.5 text-sm text-zinc-500 hover:text-zinc-900 transition-colors focus:outline-none">
                  <RefreshCw class="w-3.5 h-3.5" />
                  <span>改信息</span>
                </button>
              </div>
              <div class="space-y-4">
                <div class="space-y-1.5">
                  <Label class="text-zinc-700 text-sm font-medium">当前密码</Label>
                  <Input v-model="passwordForm.current_password" type="password" class="border-zinc-200 focus-visible:ring-zinc-900 transition-all" />
                </div>
                <div class="space-y-1.5">
                  <Label class="text-zinc-700 text-sm font-medium">新密码</Label>
                  <Input v-model="passwordForm.new_password" type="password" class="border-zinc-200 focus-visible:ring-zinc-900 transition-all" />
                </div>
                <div class="space-y-1.5">
                  <Label class="text-zinc-700 text-sm font-medium">确认新密码</Label>
                  <Input v-model="passwordForm.confirm_password" type="password" class="border-zinc-200 focus-visible:ring-zinc-900 transition-all" @keyup.enter="savePassword" />
                </div>
              </div>
              
              <Button @click="savePassword" :disabled="passwordSaving" class="w-full bg-zinc-900 hover:bg-zinc-800 text-white mt-4 h-11 transition-transform active:scale-95">
                <Loader2 v-if="passwordSaving" class="mr-2 h-4 w-4 animate-spin" />更新密码
              </Button>
            </div>
          </div>
          
        </div>
      </div>
      
      <!-- Toast Notification -->
      <Transition name="toast-slide">
        <div v-if="toastMessage" class="fixed bottom-10 left-1/2 -translate-x-1/2 z-[100] flex items-center gap-2 rounded-full bg-zinc-900 px-6 py-3 text-sm font-medium text-white shadow-xl border border-zinc-800">
          <AlertCircle v-if="isToastError" class="h-4 w-4 text-red-400" />
          <CheckCircle2 v-else class="h-4 w-4 text-emerald-400" />
          {{ toastMessage }}
        </div>
      </Transition>
    </main>
  </AppLayout>
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

/* Toast Animation */
.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.toast-slide-enter-from,
.toast-slide-leave-to {
  opacity: 0;
  transform: translate(-50%, 100%);
}
</style>
