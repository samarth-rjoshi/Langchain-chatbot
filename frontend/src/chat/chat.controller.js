import angular from 'angular';

angular.module('chatApp')
    .controller('ChatController', ['$scope', 'ChatService', '$timeout', '$rootScope', 'AuthService', '$state', function ($scope, ChatService, $timeout, $rootScope, AuthService, $state) {
        $scope.messages = [];
        $scope.userInput = '';
        $scope.isLoading = false;

        // Use AuthService for user info
        $scope.currentUser = AuthService.getCurrentUser();

        // Watch for changes in AuthService (if needed, or just rely on state reload)
        // For now, simple assignment is likely enough as controller reloads on state change
        // But if we want to be reactive:
        $scope.$watch(function () { return AuthService.getCurrentUser(); }, function (newVal) {
            $scope.currentUser = newVal;
        });

        $scope.messages.push({
            sender: 'bot',
            text: `Hello${AuthService.getCurrentUser() ? ', ' + AuthService.getCurrentUser() : ''}! I'm your Langchain chatbot. How can I help you today?`,
            time: formatTime(new Date())
        });

        $scope.sendMessage = function () {
            if (!$scope.userInput.trim()) return;

            const userMessage = {
                sender: 'user',
                text: $scope.userInput,
                time: formatTime(new Date())
            };

            $scope.messages.push(userMessage);
            const messageText = $scope.userInput;
            $scope.userInput = '';
            $scope.isLoading = true;

            $timeout(scrollToBottom, 100);

            ChatService.sendMessage(messageText)
                .then(function (response) {
                    const botMessage = {
                        sender: 'bot',
                        text: response.data.response || response.data.message || 'I received your message!',
                        time: formatTime(new Date())
                    };
                    $scope.messages.push(botMessage);
                    $scope.isLoading = false;
                    $timeout(scrollToBottom, 100);
                })
                .catch(function (error) {
                    console.error('Error:', error);
                    // Handle authentication errors
                    if (error.status === 401) {
                        // Session expired
                        const errorMessage = {
                            sender: 'bot',
                            text: 'Your session has expired. Please log in again.',
                            time: formatTime(new Date())
                        };
                        $scope.messages.push(errorMessage);

                        // Optional: Auto-redirect after a delay or let user click logout
                        // For now, we'll just show the message, or we could force logout:
                        // AuthService.logout().then(() => $state.go('login'));
                    } else {
                        const errorMessage = {
                            sender: 'bot',
                            text: 'Sorry, I encountered an error. Please try again.',
                            time: formatTime(new Date())
                        };
                        $scope.messages.push(errorMessage);
                    }
                    $scope.isLoading = false;
                    $timeout(scrollToBottom, 100);
                });
        };

        $scope.logout = function () {
            AuthService.logout().then(function () {
                $state.go('login');
            });
        };

        function formatTime(date) {
            const hours = date.getHours().toString().padStart(2, '0');
            const minutes = date.getMinutes().toString().padStart(2, '0');
            return `${hours}:${minutes}`;
        }

        function scrollToBottom() {
            const chatMessages = document.getElementById('chatMessages');
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }
    }]);



