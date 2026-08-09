
import { Card } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';

const SettingsPage = () => {
  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text">Settings</h1>
          <p className="text-sm text-muted-text">Manage system preferences and profile configurations.</p>
        </div>
      </div>

      <div className="space-y-8">
        <section>
          <h2 className="text-lg font-medium mb-3">Profile</h2>
          <Card className="p-6">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <label className="block text-muted-text mb-1">Name</label>
                <div className="font-medium">Chief Executive</div>
              </div>
              <div>
                <label className="block text-muted-text mb-1">Role</label>
                <div className="font-medium">CEO</div>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-border">
              <Button variant="outline" size="sm">Edit Profile</Button>
            </div>
          </Card>
        </section>

        <section>
          <h2 className="text-lg font-medium mb-3">Voice Assistant (Upcoming)</h2>
          <Card className="p-6">
            <div className="grid grid-cols-2 gap-4 text-sm mb-4 opacity-50">
              <div>
                <label className="block text-muted-text mb-1">Language</label>
                <div className="font-medium">English (US)</div>
              </div>
              <div>
                <label className="block text-muted-text mb-1">Voice Feedback</label>
                <div className="font-medium">Enabled</div>
              </div>
            </div>
            <div className="text-xs text-warning bg-warning/10 p-2 rounded">
              Voice settings will be activated in a future update.
            </div>
          </Card>
        </section>

        <section>
          <h2 className="text-lg font-medium mb-3">Security</h2>
          <Card className="p-6">
            <div className="space-y-3 text-sm">
              <div className="flex justify-between items-center">
                <span>Last login</span>
                <span className="text-muted-text">Today at 08:30 AM</span>
              </div>
              <div className="flex justify-between items-center">
                <span>Active Sessions</span>
                <span className="text-muted-text">1 (Current)</span>
              </div>
            </div>
          </Card>
        </section>
      </div>
    </div>
  );
};

export default SettingsPage;
