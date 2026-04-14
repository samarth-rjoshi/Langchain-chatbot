// main.js
require.config({
    baseUrl: '/src',
    paths: {
        'angular'  : '/node_modules/angular/angular',
        'ui-router': '/node_modules/@uirouter/angularjs/release/angular-ui-router'
    },
    shim: {
        'angular'  : { exports: 'angular' },
        'ui-router': { deps: ['angular'], exports: 'angular' }
    }
});

// List every single file here
require([
    'angular',
    'app',                  // 1. App module first
    'auth.service',         // 2. Services
    'chat.service',
    'login/login.controller', // 3. Controllers
    'chat/chat.controller',
    'login/login.component',  // 4. Components
    'chat/chat.component'
], function (angular) {
    // All files are loaded, now start!
    angular.bootstrap(document, ['chatApp']);
});
