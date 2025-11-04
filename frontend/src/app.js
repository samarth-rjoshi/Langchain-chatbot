import angular from 'angular';

const app = angular.module('chatApp', []);

app.run(['AuthService', '$rootScope', function(AuthService, $rootScope) {
    // Check authentication status on app start
    AuthService.checkAuth().then(function(authData) {
        $rootScope.authenticated = authData.authenticated;
        $rootScope.currentUser = authData.username || null;
    });
    
    // Expose auth functions to root scope
    $rootScope.logout = function() {
        AuthService.logout().then(function() {
            $rootScope.authenticated = false;
            $rootScope.currentUser = null;
        });
    };
}]);

