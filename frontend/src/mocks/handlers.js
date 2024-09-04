// src/mocks/handlers.js
import { http, HttpResponse } from 'msw';

// Simulate task state
const tasks = new Map();

export const handlers = [
    http.post('/flashcards/generator', () => {
        const taskId = 'mock-task-id';
        // Initialize the task WaitingComponent
        tasks.set(taskId, { progress: 0, state: 'PENDING', total: 5 });

        return HttpResponse.json({ taskId: taskId});
    }),

    http.get('/flashcards/generator/:taskId', ({ params }) => {
        const { taskId } = params;
        const task = tasks.get(taskId);

        if (!task) {
            return new HttpResponse('Task not found', { status: 404 });
        }

        // Simulate WaitingComponent
        task.progress += 1;
        // return HttpResponse.json('Testing, remove me when done!', { status: 404 })

        if (task.progress >= task.total) {
            task.state = 'SUCCESS';
            tasks.delete(taskId); // Clean up the task
            return HttpResponse.json({
                state: task.state,
                progress: task.progress,
                total: task.total,
                flashcards: [{id: 1, type: 'practice', frontSide: 'Front side mock', backSide: 'Back side mock'}] // Mock flashcards data
            });
        } else {
            return HttpResponse.json({
                state: 'PROCESSING',
                progress: task.progress,
                total: task.total
            });
        }
    }),

    http.delete('/flashcards/generator/:taskId', ({ params }) => {
        const { taskId } = params;
        const task = tasks.get(taskId);
        if (!task) {
            return new HttpResponse('Task not found', {status: 404});
        }
        return HttpResponse.json('Cancellation successful', {status: 200});
    }),

    // ... other handlers
];