% rebase('layout.tpl', title='Monitor')
<div class="jumbotron">
% for item in streams:
    <h1>{{item['name']}}</h1>
    <p>
        <img src="{{item['url']}}" style="width:1024px; height:768px" />
    </p>
% end
</div>
