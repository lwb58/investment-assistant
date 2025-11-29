/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}", // 扫描所有组件文件
  ],
  theme: {
    extend: {
      // 可选：把自定义 CSS 变量注册到 Tailwind，方便直接用 Tailwind 语法调用
      colors: {
        primary: "var(--primary-color)",
        success: "var(--success-color)",
        warning: "var(--warning-color)",
        error: "var(--error-color)",
        info: "var(--info-color)",
        text: {
          primary: "var(--text-primary)",
          secondary: "var(--text-secondary)",
          tertiary: "var(--text-tertiary)",
        },
        bg: {
          primary: "var(--bg-primary)",
          secondary: "var(--bg-secondary)",
          tertiary: "var(--bg-tertiary)",
        },
      },
      borderRadius: {
        small: "var(--border-radius-small)",
        base: "var(--border-radius-base)",
        large: "var(--border-radius-large)",
      },
      boxShadow: {
        base: "var(--shadow-base)",
        light: "var(--shadow-light)",
        medium: "var(--shadow-medium)",
      },
    },
  },
  plugins: [],
}