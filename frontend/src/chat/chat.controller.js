import angular from 'angular';

angular.module('chatApp')
    .controller('ChatController', ['$scope', 'ChatService', '$timeout', '$rootScope', 'AuthService', function($scope, ChatService, $timeout, $rootScope, AuthService) {
        $scope.messages = [];
        $scope.userInput = '';
        $scope.isLoading = false;
        
        // Bind rootScope values to scope for template access
        $scope.currentUser = $rootScope.currentUser;
        $scope.$watch(function() { return $rootScope.currentUser; }, function(newVal) {
            $scope.currentUser = newVal;
        });

        $scope.messages.push({
            sender: 'bot',
            text: `Hello${$rootScope.currentUser ? ', ' + $rootScope.currentUser : ''}! I'm your Langchain chatbot. How can I help you today?`,
            time: formatTime(new Date())
        });

        $scope.sendMessage = function() {
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
                .then(function(response) {
                    const botMessage = {
                        sender: 'bot',
                        text: response.data.response || response.data.message || 'I received your message!',
                        time: formatTime(new Date())
                    };
                    $scope.messages.push(botMessage);
                    $scope.isLoading = false;
                    $timeout(scrollToBottom, 100);
                })
                .catch(function(error) {
                    console.error('Error:', error);
                    // Handle authentication errors
                    if (error.status === 401) {
                        $rootScope.authenticated = false;
                        $rootScope.currentUser = null;
                        const errorMessage = {
                            sender: 'bot',
                            text: 'Your session has expired. Please log in again.',
                            time: formatTime(new Date())
                        };
                        $scope.messages.push(errorMessage);
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

        $scope.logout = function() {
            AuthService.logout().then(function() {
                $rootScope.authenticated = false;
                $rootScope.currentUser = null;
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



