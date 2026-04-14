// Scenario 1: Automated Incident Response — Azure infrastructure
// Creates: Log Analytics workspace, custom table, Data Collection Endpoint + Rule
// Deploy:  az deployment group create -g <rg> -f infra/scenario1.bicep -p infra/scenario1.bicepparam
// Destroy: az group delete -n <rg> --yes --no-wait

targetScope = 'resourceGroup'

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Log Analytics workspace name')
param workspaceName string = 'mcp-demo-logs'

@description('Data Collection Endpoint name')
param dceName string = 'mcp-demo-dce'

@description('Data Collection Rule name')
param dcrName string = 'mcp-demo-dcr'

@description('Custom table name (without the _CL suffix)')
param customTableName string = 'CheckoutErrors'

// Log Analytics Workspace
resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: workspaceName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Custom log table for checkout service errors
resource customTable 'Microsoft.OperationalInsights/workspaces/tables@2022-10-01' = {
  parent: workspace
  name: '${customTableName}_CL'
  properties: {
    schema: {
      name: '${customTableName}_CL'
      columns: [
        { name: 'TimeGenerated', type: 'datetime', description: 'Event timestamp' }
        { name: 'status', type: 'int', description: 'HTTP status code' }
        { name: 'service', type: 'string', description: 'Service name' }
        { name: 'error', type: 'string', description: 'Error message' }
        { name: 'transaction_id', type: 'string', description: 'Transaction identifier' }
        { name: 'severity', type: 'string', description: 'Log severity level' }
        { name: 'stack_trace', type: 'string', description: 'Error stack trace' }
      ]
    }
    retentionInDays: 30
    totalRetentionInDays: 30
  }
}

// Data Collection Endpoint — ingestion target for the DCR
resource dce 'Microsoft.Insights/dataCollectionEndpoints@2023-03-11' = {
  name: dceName
  location: location
  properties: {
    networkAcls: {
      publicNetworkAccess: 'Enabled'
    }
  }
}

// Data Collection Rule — routes ingested logs to the custom table
resource dcr 'Microsoft.Insights/dataCollectionRules@2023-03-11' = {
  name: dcrName
  location: location
  properties: {
    dataCollectionEndpointId: dce.id
    streamDeclarations: {
      'Custom-${customTableName}_CL': {
        columns: [
          { name: 'TimeGenerated', type: 'datetime' }
          { name: 'status', type: 'int' }
          { name: 'service', type: 'string' }
          { name: 'error', type: 'string' }
          { name: 'transaction_id', type: 'string' }
          { name: 'severity', type: 'string' }
          { name: 'stack_trace', type: 'string' }
        ]
      }
    }
    destinations: {
      logAnalytics: [
        {
          workspaceResourceId: workspace.id
          name: 'logAnalyticsDest'
        }
      ]
    }
    dataFlows: [
      {
        streams: [ 'Custom-${customTableName}_CL' ]
        destinations: [ 'logAnalyticsDest' ]
        transformKql: 'source'
        outputStream: 'Custom-${customTableName}_CL'
      }
    ]
  }
}

// Outputs used by deploy/inject scripts
output workspaceId string = workspace.properties.customerId
output workspaceName string = workspace.name
output workspaceResourceId string = workspace.id
output dceEndpoint string = dce.properties.logsIngestion.endpoint
output dcrImmutableId string = dcr.properties.immutableId
output dcrId string = dcr.id
output customTableName string = '${customTableName}_CL'
