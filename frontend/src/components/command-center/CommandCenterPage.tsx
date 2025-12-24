import { useEffect } from 'react';
import { useCommandCenterStore } from '../../store/commandCenterStore';
import { SupervisorList } from './SupervisorList';
import { ResultList } from './ResultList';
import { CommandInputBar } from './CommandInputBar';

export function CommandCenterPage() {
  const {
    supervisors,
    selectedSupervisorId,
    command,
    mainFeed,
    resultsBySupervisor,
    loading,
    error,
    init,
    setSelectedSupervisor,
    setCommand,
    sendCommand,
  } = useCommandCenterStore();

  useEffect(() => {
    void init();
  }, [init]);

  const selectedResults = selectedSupervisorId
    ? resultsBySupervisor[selectedSupervisorId] ?? []
    : [];

  return (
    <div className="h-full flex flex-col bg-slate-950 text-slate-100">
      <div className="flex-1 grid grid-cols-12 gap-4 p-4">
        <aside className="col-span-3 border border-slate-800 rounded-lg p-3 bg-slate-900/60 flex flex-col">
          <h2 className="text-sm font-semibold mb-2">Supervisors</h2>
          <SupervisorList
            supervisors={supervisors}
            selectedId={selectedSupervisorId}
            onSelect={setSelectedSupervisor}
          />
        </aside>

        <main className="col-span-5 border border-slate-800 rounded-lg p-3 bg-slate-900/60 flex flex-col">
          <ResultList title="Main output" results={mainFeed} />
        </main>

        <section className="col-span-4 border border-slate-800 rounded-lg p-3 bg-slate-900/60 flex flex-col">
          <ResultList
            title={selectedSupervisorId ? 'Selected supervisor output' : 'Select a supervisor'}
            results={selectedResults}
          />
        </section>
      </div>

      <div className="border-t border-slate-900 bg-slate-950 px-4 py-3">
        {error && <div className="text-xs text-red-400 mb-1">{error}</div>}
        <CommandInputBar
          supervisors={supervisors}
          selectedId={selectedSupervisorId}
          command={command}
          loading={loading}
          onSelect={setSelectedSupervisor}
          onChangeCommand={setCommand}
          onSend={sendCommand}
        />
      </div>
    </div>
  );
}
