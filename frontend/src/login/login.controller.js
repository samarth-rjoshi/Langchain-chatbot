import angular from 'angular';

angular.module('chatApp')
    .controller('LoginController', ['$scope', 'AuthService', '$rootScope', function($scope, AuthService, $rootScope) {
        $scope.username = '';
        $scope.password = '';
        $scope.error = '';
        $scope.isLoading = false;

        $scope.login = function() {
            if (!$scope.username.trim() || !$scope.password.trim()) {
                $scope.error = 'Please enter both username and password';
                return;
            }

            $scope.error = '';
            $scope.isLoading = true;

            AuthService.login($scope.username, $scope.password)
                .then(function(response) {
                    $scope.isLoading = false;
                    $rootScope.authenticated = true;
                    $rootScope.currentUser = response.username;
                })
                .catch(function(error) {
                    $scope.isLoading = false;
                    $scope.error = error.message || error.error || 'Login failed. Please try again.';
                });
        };

        $scope.handleKeyPress = function(event) {
            if (event.key === 'Enter') {
                $scope.login();
            }
        };
    }]);


