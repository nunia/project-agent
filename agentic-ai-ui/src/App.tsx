import { useState } from 'react';
import { MessagesSquare, Send, Mic } from 'lucide-react'; 
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from '@/lib/utils';
import { marked } from 'marked';  

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);  // State to track microphone status

  // Initialize SpeechRecognition (for voice-to-text)
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'en-US';
  recognition.continuous = false;

  // Function to start listening to voice
  const startListening = () => {
    recognition.start();
    setIsListening(true);
  };

  // Function to stop listening to voice
  const stopListening = () => {
    recognition.stop();
    setIsListening(false);
  };

  // Handle the speech recognition results
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    setInput(transcript);  // Update input with the transcribed text
  };

  // Handle the speech recognition error
  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
    setIsListening(false);  // Stop listening if there's an error
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const encodedMessage = encodeURIComponent(userMessage);
      const response = await fetch(`http://localhost:8000/openai/agent4?message=${encodedMessage}`, {
        method: 'POST',
        headers: {
          'accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Access the value of the key 'Nunia.AI'
      const content = data['Nunia.AI'] || 'Sorry, no response from AI.';

      // Parse bold markdown syntax to HTML
      const parsedContent = marked(content);

      // Add assistant response to chat
      setMessages(prev => [...prev, { role: 'assistant', content: parsedContent }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error while processing your request. Please make sure the API server is running at http://localhost:8000' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-neutral-100 dark:from-neutral-950 dark:to-neutral-900 p-4 sm:p-8">
      <Card className="container mx-auto max-w-4xl h-[600px] flex flex-col">
        {/* Header */}
        <div className="flex items-center gap-2 p-4 border-b">
          <MessagesSquare className="w-6 h-6 text-primary" />
          <h1 className="text-xl font-semibold">AI Assistant</h1>
        </div>

        {/* Chat Area */}
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-muted-foreground py-8">
                Start a conversation by typing a message below
              </div>
            )}
            {messages.map((message, index) => (
              <div
                key={index}
                className={cn(
                  "flex w-full",
                  message.role === 'assistant' ? "justify-start" : "justify-end"
                )}
              >
                <div
                  className={cn(
                    "rounded-lg px-4 py-2 max-w-[80%]",
                    message.role === 'assistant' 
                      ? "bg-muted" 
                      : "bg-primary text-primary-foreground"
                  )}
                  dangerouslySetInnerHTML={{ __html: message.content }}  // Render HTML safely
                />
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-lg px-4 py-2">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 rounded-full bg-primary animate-bounce" />
                    <div className="w-2 h-2 rounded-full bg-primary animate-bounce [animation-delay:0.2s]" />
                    <div className="w-2 h-2 rounded-full bg-primary animate-bounce [animation-delay:0.4s]" />
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Input Area */}
        <form onSubmit={sendMessage} className="p-4 border-t flex gap-2">
          <Input
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1"
          />
          <Button type="submit" disabled={isLoading}>
            <Send className="w-4 h-4 mr-2" />
            Send
          </Button>
          {/* Mic button to start voice recognition */}
          <Button 
            type="button" 
            onClick={isListening ? stopListening : startListening} 
            disabled={isLoading}
            className="flex items-center"
          >
            <Mic className={`w-4 h-4 mr-2 ${isListening ? 'text-red-500' : 'text-gray-500'}`} />
            {isListening ? 'Stop Listening' : 'Start Listening'}
          </Button>
        </form>
      </Card>
    </div>
  );
}

export default App;
