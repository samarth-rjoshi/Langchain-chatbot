import angular from 'angular';

angular.module('chatApp')
    .controller('ChatController', ['$scope', 'ChatService', '$timeout', 'AuthService', '$state', '$http', '$sce', function ($scope, ChatService, $timeout, AuthService, $state, $http, $sce) {
        const vm = this;
        $scope.messages = [];
        $scope.userInput = '';
        $scope.isLoading = false;
        $scope.conversations = [];
        $scope.currentConversation = null;
        $scope.isStreaming = false;
        $scope.showPanel = true;

        // Use AuthService for user info
        $scope.currentUser = AuthService.getCurrentUser();

        $scope.initUser = function () {
            $http.get('http://localhost:8000/user_threads', { withCredentials: true })
                .then(response => {
                    const data = response.data;
                    $scope.userId = data.userId;
                    if (data.threads && data.threads.length > 0) {
                        $scope.conversations = [];

                        data.threads.sort((a, b) => {
                            const dateA = new Date(a.timestamp);
                            const dateB = new Date(b.timestamp);
                            return dateB - dateA;
                        });

                        data.threads.forEach(thread => {
                            $scope.conversations.push({
                                id: thread.thread_id,
                                name: thread.headline || 'New Conversation',
                                timestamp: thread.timestamp,
                                messages: [],
                                userId: $scope.userId
                            });
                        });
                        $scope.currentConversation = $scope.conversations[0];
                        $scope.selectConversation($scope.currentConversation);
                    } else {
                        $scope.createNewChat();
                    }
                })
                .catch(error => {
                    console.error('Failed to load conversations:', error);
                });
        };

        $scope.createNewChat = function () {
            const newId = crypto.randomUUID();
            const currentTime = new Date();
            const newConversation = {
                id: newId,
                name: "New Conversation",
                lastMessage: '',
                timestamp: currentTime,
                messages: [],
            };
            $scope.conversations.unshift(newConversation);
            $scope.currentConversation = newConversation;
            $scope.messages = [];

            // Initial bot message
            $scope.messages.push({
                sender: 'bot',
                text: $sce.trustAsHtml(`Hello${AuthService.getCurrentUser() ? ', ' + AuthService.getCurrentUser() : ''}! I'm your Langchain chatbot. How can I help you today?`),
                time: formatTime(new Date())
            });
        };

        $scope.selectConversation = function (conversation) {
            $scope.currentConversation = conversation;
            $scope.isLoading = true;

            $http.post('http://localhost:8000/thread_history', {
                thread_id: conversation.id,
            }, { withCredentials: true })
                .then(response => {
                    const data = response.data;
                    $scope.messages = [];

                    if (data.error) {
                        console.error("Error loading history:", data.error);
                    } else {
                        for (let i = 0; i < data.question.length; i++) {
                            // Add user message
                            $scope.messages.push({
                                sender: 'user',
                                text: data.question[i],
                                time: formatTime(new Date(data.timestamp || Date.now())) // Timestamp might be per message ideally
                            });

                            // Add bot message
                            if (i < data.generation.length) {
                                $scope.messages.push({
                                    sender: 'bot',
                                    text: $sce.trustAsHtml(data.generation[i]),
                                    time: formatTime(new Date(data.timestamp || Date.now()))
                                });
                            }
                        }
                    }

                    if ($scope.messages.length === 0) {
                        $scope.messages.push({
                            sender: 'bot',
                            text: $sce.trustAsHtml(`Hello${AuthService.getCurrentUser() ? ', ' + AuthService.getCurrentUser() : ''}! I'm your Langchain chatbot. How can I help you today?`),
                            time: formatTime(new Date())
                        });
                    }

                    $timeout(scrollToBottom, 100);
                })
                .catch(error => {
                    console.error('Error:', error);
                })
                .finally(() => {
                    $scope.isLoading = false;
                });
        };

        $scope.deleteConversation = function (conversation, event) {
            if (event) event.stopPropagation();

            if (!confirm('Are you sure you want to delete this conversation?')) return;

            $http.post('http://localhost:8000/delete_thread', {
                thread_id: conversation.id
            }, { withCredentials: true })
                .then(response => {
                    if (response.data.success) {
                        const index = $scope.conversations.findIndex(c => c.id === conversation.id);
                        if (index > -1) {
                            $scope.conversations.splice(index, 1);
                            if ($scope.currentConversation && $scope.currentConversation.id === conversation.id) {
                                if ($scope.conversations.length > 0) {
                                    $scope.selectConversation($scope.conversations[0]);
                                } else {
                                    $scope.createNewChat();
                                }
                            }
                        }
                    }
                })
                .catch(error => console.error('Error deleting thread:', error));
        };

        $scope.handleKeydown = function (event) {
            if (event.keyCode === 13 && !event.shiftKey) {
                event.preventDefault();
                $scope.sendMessage();
            }
            // Auto-resize
            const textarea = event.target;
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
        };

        $scope.sendMessage = function () {
            if (!$scope.userInput.trim() || $scope.isStreaming) return;

            const userMessageText = $scope.userInput;
            const userMessage = {
                sender: 'user',
                text: userMessageText,
                time: formatTime(new Date())
            };

            $scope.messages.push(userMessage);
            $scope.userInput = '';

            // Reset textarea height
            setTimeout(() => {
                const textarea = document.querySelector('.chat-input');
                if (textarea) textarea.style.height = 'auto';
            }, 0);

            $scope.isLoading = true;
            $scope.isStreaming = true;

            $timeout(scrollToBottom, 100);

            // Ensure we have a current conversation
            if (!$scope.currentConversation) {
                $scope.createNewChat();
            }

            const threadId = $scope.currentConversation.id;

            // Create placeholder for bot message
            const botMessage = {
                sender: 'bot',
                text: '',
                time: formatTime(new Date()),
                isLoading: true
            };
            $scope.messages.push(botMessage);

            // Send message to backend
            $http.post('http://localhost:8000/query', {
                question: userMessageText,
                thread_id: threadId
            }, { withCredentials: true })
                .then(function (response) {
                    const data = response.data;
                    if (data.answer) {
                        botMessage.text = $sce.trustAsHtml(data.answer);
                        botMessage.isLoading = false;
                    } else if (data.error) {
                        botMessage.text = $sce.trustAsHtml("Error: " + data.error);
                        botMessage.isLoading = false;
                    }
                    $scope.isStreaming = false;
                    // Update conversation name if it's new and we got a headline
                    if ($scope.currentConversation.name === 'New Conversation' && data.headline) {
                        $scope.currentConversation.name = data.headline;
                        // Update in the list as well
                        const conv = $scope.conversations.find(c => c.id === threadId);
                        if (conv) {
                            conv.name = data.headline;
                        }
                    }
                    $timeout(scrollToBottom, 100);
                })
                .catch(function (error) {
                    console.error("Error sending message:", error);
                    botMessage.text = $sce.trustAsHtml("Sorry, I encountered an error. Please try again.");
                    botMessage.isLoading = false;
                    $scope.isStreaming = false;
                    $timeout(scrollToBottom, 100);
                })
                .finally(() => {
                    $scope.isLoading = false;
                });
        };

        $scope.logout = function () {
            AuthService.logout().then(function () {
                $state.go('login');
            });
        };

        $scope.togglePanel = function () {
            $scope.showPanel = !$scope.showPanel;
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

        // Initialize
        $scope.initUser();
    }]);
