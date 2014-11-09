module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n',
        preserveComments: 'some',
      },
      build: {
        files: {
          'core/static/account.min.js': [
            'core/static/js/lib/jquery-2.1.1.min.js',
            'core/static/js/lib/bootstrap-3.1.1.min.js',
            'core/static/js/base.js',
          ],
        }
      }
    },
    cssmin: {
      combine: {
        options: {
          banner: '/* My minified css file */'
        },
        files: {
          'core/static/account.min.css': [
            'core/static/css/lib/bootstrap-3.1.1.min.css',
            'core/static/css/lib/bootstrap-theme-3.1.1.min.css',
            'core/static/css/base.css',
          ],
        },
      },
    },
  });

  // Load tasks
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-cssmin');

  // Default task(s).
  grunt.registerTask('default', ['uglify']);

};
