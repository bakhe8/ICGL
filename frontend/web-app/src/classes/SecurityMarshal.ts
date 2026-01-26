import type { Marshal } from '../interfaces/Marshal';

export class SecurityMarshal implements Marshal {
    executeTask(task: string): void {
        console.log(`Executing security task: ${task}`);
    }
}