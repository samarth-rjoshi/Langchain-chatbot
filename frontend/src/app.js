define(['angular', 'ui-router'], function (angular) {

    var app = angular.module('chatApp', ['ui.router']);

    app.config(['$stateProvider', '$urlServiceProvider', function ($stateProvider, $urlServiceProvider) {
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

        $urlServiceProvider.rules.otherwise('/login');
    }]);

    app.run(['AuthService', '$transitions', '$state', function (AuthService, $transitions, $state) {
        AuthService.checkAuth().then(function (authData) {
            if (authData.authenticated) {
                $state.go('chat');
            } else {
                $state.go('login');
            }
        });

        $transitions.onStart({}, function (trans) {
            const toState = trans.to();
            const requiresAuth = toState.data && toState.data.requiresAuth;
            if (requiresAuth && !AuthService.isAuthenticated()) {
                return trans.router.stateService.target('login');
            }
        });
    }]);

    return app;
});

