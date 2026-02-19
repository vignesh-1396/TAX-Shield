'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { Copy, Trash2, Key, Plus, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { useAuth } from '@/app/context/AuthContext';
import api from '@/lib/api';

export default function APIKeysPage() {
    const { user } = useAuth();
    const [apiKeys, setApiKeys] = useState([]);
    const [loading, setLoading] = useState(true);
    const [creating, setCreating] = useState(false);
    const [newKeyName, setNewKeyName] = useState('');
    const [newKeyData, setNewKeyData] = useState(null);
    const [showNewKey, setShowNewKey] = useState(false);

    useEffect(() => {
        loadAPIKeys();
    }, []);

    const loadAPIKeys = async () => {
        try {
            setLoading(true);
            const response = await api.get('/api-keys');
            setApiKeys(response.data);
        } catch (error) {
            console.error('Failed to load API keys:', error);
        } finally {
            setLoading(false);
        }
    };

    const createAPIKey = async () => {
        if (!newKeyName.trim()) {
            alert('Please enter a key name');
            return;
        }

        try {
            setCreating(true);
            const response = await api.post('/api-keys', {
                key_name: newKeyName,
                expires_in_days: null, // No expiration
                permissions: 'read,write'
            });

            setNewKeyData(response.data);
            setShowNewKey(true);
            setNewKeyName('');
            await loadAPIKeys();
        } catch (error) {
            console.error('Failed to create API key:', error);
            alert('Failed to create API key');
        } finally {
            setCreating(false);
        }
    };

    const revokeAPIKey = async (keyId) => {
        if (!confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) {
            return;
        }

        try {
            await api.delete(`/api-keys/${keyId}`);
            await loadAPIKeys();
        } catch (error) {
            console.error('Failed to revoke API key:', error);
            alert('Failed to revoke API key');
        }
    };

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        alert('Copied to clipboard!');
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'Never';
        return new Date(dateString).toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="container mx-auto p-6 max-w-6xl">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">API Keys</h1>
                <p className="text-gray-600">
                    Manage API keys for integrating ITC Shield with Tally and other applications
                </p>
            </div>

            {/* New Key Alert */}
            {newKeyData && showNewKey && (
                <Card className="mb-6 border-green-500 bg-green-50">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-green-700">
                            <Key className="h-5 w-5" />
                            API Key Created Successfully
                        </CardTitle>
                        <p className="text-sm text-green-600">
                            <strong>IMPORTANT:</strong> Copy this key now. You won't be able to see it again!
                        </p>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center gap-2 mb-4">
                            <Input
                                value={newKeyData.api_key}
                                readOnly
                                className="font-mono text-sm"
                            />
                            <Button
                                onClick={() => copyToClipboard(newKeyData.api_key)}
                                variant="outline"
                            >
                                <Copy className="h-4 w-4 mr-2" />
                                Copy
                            </Button>
                        </div>
                        <Button
                            onClick={() => {
                                setShowNewKey(false);
                                setNewKeyData(null);
                            }}
                            variant="secondary"
                            size="sm"
                        >
                            I've saved my key
                        </Button>
                    </CardContent>
                </Card>
            )}

            {/* Create New Key */}
            <Card className="mb-6">
                <CardHeader>
                    <CardTitle>Create New API Key</CardTitle>
                    <p className="text-sm text-gray-500">
                        Generate a new API key for Tally integration or API access
                    </p>
                </CardHeader>
                <CardContent>
                    <div className="flex gap-2">
                        <Input
                            placeholder="Key name (e.g., 'Tally Production', 'Development')"
                            value={newKeyName}
                            onChange={(e) => setNewKeyName(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && createAPIKey()}
                            className="flex-1"
                        />
                        <Button
                            onClick={createAPIKey}
                            disabled={creating || !newKeyName.trim()}
                        >
                            <Plus className="h-4 w-4 mr-2" />
                            {creating ? 'Creating...' : 'Create Key'}
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Existing Keys */}
            <Card>
                <CardHeader>
                    <CardTitle>Your API Keys</CardTitle>
                    <p className="text-sm text-gray-500">
                        {apiKeys.length} active key{apiKeys.length !== 1 ? 's' : ''}
                    </p>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div className="text-center py-8 text-gray-500">Loading...</div>
                    ) : apiKeys.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                            <Key className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                            <p>No API keys yet</p>
                            <p className="text-sm">Create your first key to get started</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {apiKeys.map((key) => (
                                <div
                                    key={key.id}
                                    className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2 mb-2">
                                                <h3 className="font-semibold">{key.key_name}</h3>
                                                {key.is_active ? (
                                                    <Badge variant="success" className="bg-green-100 text-green-700">
                                                        Active
                                                    </Badge>
                                                ) : (
                                                    <Badge variant="secondary">Revoked</Badge>
                                                )}
                                            </div>

                                            <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                                                <div>
                                                    <span className="font-medium">Key:</span>{' '}
                                                    <code className="bg-gray-100 px-2 py-1 rounded">
                                                        {key.prefix}...
                                                    </code>
                                                </div>
                                                <div>
                                                    <span className="font-medium">Created:</span>{' '}
                                                    {formatDate(key.created_at)}
                                                </div>
                                                <div>
                                                    <span className="font-medium">Last Used:</span>{' '}
                                                    {formatDate(key.last_used_at)}
                                                </div>
                                                <div>
                                                    <span className="font-medium">Usage:</span>{' '}
                                                    {key.usage_count} calls
                                                </div>
                                            </div>
                                        </div>

                                        <div className="flex gap-2">
                                            {key.is_active && (
                                                <Button
                                                    onClick={() => revokeAPIKey(key.id)}
                                                    variant="destructive"
                                                    size="sm"
                                                >
                                                    <Trash2 className="h-4 w-4 mr-2" />
                                                    Revoke
                                                </Button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Usage Instructions */}
            <Card className="mt-6">
                <CardHeader>
                    <CardTitle>How to Use API Keys</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div>
                        <h4 className="font-semibold mb-2">For Tally Integration:</h4>
                        <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600">
                            <li>Create a new API key above</li>
                            <li>Copy the generated key (shown only once!)</li>
                            <li>Open your Tally TDL file: <code className="bg-gray-100 px-1">ITCShield_SaaS_Integration.TDL</code></li>
                            <li>Paste the key in the <code className="bg-gray-100 px-1">ITCShield_API_Key</code> variable</li>
                            <li>Save and reload Tally</li>
                        </ol>
                    </div>

                    <div>
                        <h4 className="font-semibold mb-2">For API Access:</h4>
                        <p className="text-sm text-gray-600 mb-2">
                            Include the API key in the Authorization header:
                        </p>
                        <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto">
                            {`Authorization: Bearer YOUR_API_KEY`}
                        </pre>
                    </div>

                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <div className="flex gap-2">
                            <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0" />
                            <div className="text-sm">
                                <p className="font-semibold text-yellow-800 mb-1">Security Best Practices:</p>
                                <ul className="list-disc list-inside space-y-1 text-yellow-700">
                                    <li>Never share your API keys publicly</li>
                                    <li>Revoke keys immediately if compromised</li>
                                    <li>Use different keys for development and production</li>
                                    <li>Rotate keys regularly (every 90 days recommended)</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
