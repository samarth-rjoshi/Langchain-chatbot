import angular from 'angular';
import uiRouter from '@uirouter/angularjs';

const app = angular.module('chatApp', [uiRouter]);

app.config(['$stateProvider', '$urlServiceProvider', function($stateProvider, $urlServiceProvider) {
    $stateProvider
        .state('login', {
            url: '/login',
            template: '<login-widget></login-widget>'
        })
        .state('chat', {
            url: '/chat',
            template: '<chat-widget></chat-widget>',
            data: { requiresAuth: true }
        });

    // Default route
    $urlServiceProvider.rules.otherwise('/login');
}]);

app.run(['AuthService', '$rootScope', '$transitions', '$state', function(AuthService, $rootScope, $transitions, $state) {
    // Check authentication status on app start
    AuthService.checkAuth().then(function(authData) {
        $rootScope.authenticated = authData.authenticated;
        $rootScope.currentUser = authData.username || null;
        // Redirect based on auth status
        if (authData.authenticated) {
            $state.go('chat');
        } else {
            $state.go('login');
        }
    });

    // Expose auth functions to root scope
    $rootScope.logout = function() {
        AuthService.logout().then(function() {
            $rootScope.authenticated = false;
            $rootScope.currentUser = null;
            $state.go('login');
        });
    };

    // Transition guard: redirect to login if state requires auth
    $transitions.onStart({}, function(trans) {
        const toState = trans.to();
        const requiresAuth = toState.data && toState.data.requiresAuth;
        if (requiresAuth && !AuthService.isAuthenticated()) {
            return trans.router.stateService.target('login');
        }
    });
}]);

