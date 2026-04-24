import { createRouter, createWebHistory } from "vue-router"

import CoursePreview from "@/views/CoursePreview.vue"
import CourseView from "@/views/CourseView.vue"

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "course-home", component: CourseView },
    { path: "/preview", name: "course-preview", component: CoursePreview },
  ],
})
