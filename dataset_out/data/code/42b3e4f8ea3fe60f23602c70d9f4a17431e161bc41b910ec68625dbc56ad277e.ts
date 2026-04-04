export const window = {
  showInformationMessage: (_message: string): void => {
    // No-op stub for tests running outside VS Code.
  },
};

export type Disposable = { dispose(): void };
