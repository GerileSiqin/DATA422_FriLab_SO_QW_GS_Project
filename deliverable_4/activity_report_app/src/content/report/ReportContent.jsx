import React from 'react';
import { ReportSection, RichNarrative, useDataApp } from '../../data-app-public.jsx';
import text from './activity-text.json';
export function ReportContent() {
  const { snapshot, visible } = useDataApp();
  return <article className="report-content" aria-label="Deliverable 4 activities and outcomes">
    {visible('activity-report') && <ReportSection id="activity-report" title="Deliverable 4 activities and outcomes" queryId="cleaning_results" sourceRows={snapshot.queries.cleaning_results.rows} showHeading={false}>
      <RichNarrative id="activity-report:body" value={text} label="Edit activity report" />
    </ReportSection>}
  </article>;
}
