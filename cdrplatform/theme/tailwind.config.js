/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["../../templates/**/*.html", "../../cdrplatform/**/*.{html,py}"],
  theme: {
    extend: {},
  },
  plugins: [require("@tailwindcss/forms")],
};
