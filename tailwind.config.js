const colors = require('./colors.json');

module.exports = {
  content: [
    './app/templates/**/*.html',
    './app/static/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: colors,
      boxShadow: {
        'white': '0 4px 6px rgba(255, 255, 255, 0.1)', // Custom shadow
      },
    },
  },
  plugins: [],
};
