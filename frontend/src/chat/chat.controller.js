import angular from 'angular';

angular.module('chatApp')
    .controller('ChatController', ['$scope', 'ChatService', '$timeout', function($scope, ChatService, $timeout) {
        $scope.messages = [];
        $scope.userInput = '';
        $scope.isLoading = false;

        $scope.messages.push({
            sender: 'bot',
            text: 'Hello! I\'m your Langchain chatbot. How can I help you today?',
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
                    const errorMessage = {
                        sender: 'bot',
                        text: 'Sorry, I encountered an error. Please try again.',
                        time: formatTime(new Date())
                    };
                    $scope.messages.push(errorMessage);
                    $scope.isLoading = false;
                    $timeout(scrollToBottom, 100);
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


