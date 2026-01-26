import type { Architect } from '../interfaces/Architect';

export class ProjectArchitect implements Architect {
    defineMarshals(): string[] {
        // Define the list of specialized Marshals
        return ['SecurityMarshal', 'DataMarshal', 'ComplianceMarshal'];
    }

    defineGovernanceType(): string {
        // Define the type of governance
        return 'Strict';
    }
}