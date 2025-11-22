import angular from 'angular';

angular.module('chatApp')
    .controller('LoginController', ['$scope', 'AuthService', '$rootScope', '$state', function ($scope, AuthService, $rootScope, $state) {
        $scope.credentials = {
            username: '',
            password: '',
            email: ''
        };
        $scope.isSignup = false; // Toggle state
        $scope.error = '';
        $scope.isLoading = false;

        // If already authenticated, go to chat
        if ($rootScope.authenticated) {
            $state.go('chat');
            return;
        }

        $scope.toggleSignup = function () {
            $scope.isSignup = !$scope.isSignup;
            $scope.error = '';
            $scope.credentials = {
                username: '',
                password: '',
                email: ''
            };
        };

        $scope.submit = function () {
            if (!$scope.credentials.username.trim() || !$scope.credentials.password.trim()) {
                $scope.error = 'Please enter username and password';
                return;
            }

            if ($scope.isSignup && !$scope.credentials.email.trim()) {
                $scope.error = 'Please enter email for signup';
                return;
            }

            $scope.error = '';
            $scope.isLoading = true;

            if ($scope.isSignup) {
                AuthService.register($scope.credentials.email, $scope.credentials.username, $scope.credentials.password)
                    .then(function (response) {
                        $scope.isLoading = false;
                        $scope.isSignup = false; // Switch to login after success
                        $scope.error = 'Account created! Please log in.';
                        $scope.credentials.password = ''; // Clear password
                    })
                    .catch(function (error) {
                        $scope.isLoading = false;
                        $scope.error = error.message || error.error || 'Signup failed. Please try again.';
                    });
            } else {
                AuthService.login($scope.credentials.username, $scope.credentials.password)
                    .then(function (response) {
                        $scope.isLoading = false;
                        $rootScope.authenticated = true;
                        $rootScope.currentUser = response.username;
                        // Navigate to chat state
                        $state.go('chat');
                    })
                    .catch(function (error) {
                        $scope.isLoading = false;
                        $scope.error = error.message || error.error || 'Login failed. Please try again.';
                    });
            }
        };

        $scope.handleKeyPress = function (event) {
            if (event.key === 'Enter') {
                $scope.submit();
            }
        };
    }]);


