import { createRouter, createWebHistory } from "vue-router"
import Home from "@/views/Home.vue"
import Login from "@/views/Login.vue"
import ResumeList from "@/views/ResumeList.vue"
import ResumeEditor from "@/views/ResumeEditor.vue"
import TemplateGallery from "@/views/TemplateGallery.vue"
import Profile from "@/views/Profile.vue"

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: Home },
    { path: "/login", component: Login },
    { path: "/register", component: Login }, // Merged with Login component
    { path: "/resumes", component: ResumeList },
    { path: "/resumes/:id/edit", component: ResumeEditor },
    { path: "/templates", component: TemplateGallery },
    { path: "/profile", component: Profile },
  ],
})

router.beforeEach((to) => {
  const publicPages = ["/", "/login", "/register", "/templates"]
  const token = localStorage.getItem("vitaflow_token")
  if (!publicPages.includes(to.path) && !token) return "/login"
})

export default router
