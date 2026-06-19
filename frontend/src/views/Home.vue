<script setup lang="ts">
import AppLayout from "@/components/layout/AppLayout.vue"
import HeroSection from "@/components/home/HeroSection.vue"
import FeatureSection from "@/components/home/FeatureSection.vue"
import TemplateShowcase from "@/components/home/TemplateShowcase.vue"
import WorkflowSection from "@/components/home/WorkflowSection.vue"
</script>
<template>
  <AppLayout>
    <main class="flex-1 bg-[#fafafa]">
      <HeroSection />
      <FeatureSection />
      <TemplateShowcase />
      <WorkflowSection />
    </main>
    <footer class="bg-zinc-50 border-t border-zinc-200 px-4 py-8 sm:px-6 sm:py-12 text-center">
      <p class="text-sm text-zinc-500 mb-2">
        VitaFlow 简历流 · 你的经历，值得更好的表达。
      </p>
      <div class="text-xs text-zinc-400 flex flex-col sm:flex-row items-center justify-center gap-1 sm:gap-3">
        <span>&copy; 2026 GeekZero</span>
        <span class="hidden sm:inline">|</span>
        <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer" class="hover:text-zinc-600 transition-colors">
          鲁ICP备2023002307号-2
        </a>
      </div>
    </footer>
  </AppLayout>
</template>
