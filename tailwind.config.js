/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#fef3f2",
          100: "#fde6e3",
          200: "#fdd1cc",
          300: "#fbb0a8",
          400: "#f68275",
          500: "#ec5a49",
          600: "#d93d2b",
          700: "#b63021",
          800: "#972b1f",
          900: "#7d2921",
          950: "#44110c",
        },
        warm: {
          50: "#fdf8f0",
          100: "#fbeedd",
          200: "#f6d9b8",
          300: "#f0be8a",
          400: "#e99a59",
          500: "#e37f36",
          600: "#d4662b",
          700: "#b04e25",
          800: "#8d3f24",
          900: "#723520",
          950: "#3d190f",
        },
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
  ],
};
